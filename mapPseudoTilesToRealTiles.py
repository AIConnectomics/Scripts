# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 14:22:26 2016

@author: ariaj
"""

import json
import xml.etree.ElementTree as ET
import numpy as np
import scipy.misc
import SimpleITK as sitk

def itk_imread(fn):
    r = sitk.ImageFileReader()
    r.SetFileName(fn)
    I = r.Execute()
    del r
    return sitk.GetArrayFromImage(I)

# this figures out the bounding box on the mask -- use to figure out where 
# the pseudoTiles are relative to the realTiles. This is adapted from original fcn
def getShiftToRealCoordSpace(filename):
    reader = sitk.ImageFileReader( )
    reader.SetFileName (filename)
    image = reader.Execute( )
    mask = itk_imread(filename)[0].astype('bool')
    resampled = scipy.misc.imresize(
                        mask, mask.shape, interp='nearest').astype('bool')
    unm = np.argwhere(resampled)
    vtx_0 = unm.min(0)
    del reader
    del image
    del mask
    del resampled
    del unm
    return vtx_0[1], vtx_0[0] #return xMin, yMin

# this function determines if a realTile is in a pseudoTile
def realTileInPseudoTile(realTile, pseudoTile):
    # the mapping of the realTiles after nonlinear transformation matches 
    #TrakEM's output within a certain bound of pixels    
    extraAllowance = 600 
    realTileX = realTile.xMin, realTile.xMax
    realTileY = realTile.yMin, realTile.yMax
    pseudoTileX = pseudoTile.xMin - extraAllowance, pseudoTile.xMax + \
                    extraAllowance
    pseudoTileY = pseudoTile.yMin - extraAllowance, pseudoTile.yMax + \
                    extraAllowance
    xOverLap = min(realTileX[-1], pseudoTileX[-1] + 1) - \
                max(realTileX[0], pseudoTileX[0]) 
    yOverLap = min(realTileY[-1], pseudoTileY[-1] + 1) - \
                max(realTileY[0], pseudoTileY[0]) 
    if xOverLap > 0 and yOverLap > 0 :
        return True
    else:
        return False

# this is the function that's employed by the TrakEM2 software
def kernelExpand(position, nonLinearTrans):
    expanded = np.zeros(nonLinearTrans.length)
    counter = 0
    
    for i in range(1, nonLinearTrans.dimension+1):
        for j in range(i, 0, -1):
            expanded[counter] = (np.power(position[0], j)) * \
                                (np.power(position[1], i - j))
            counter += 1
            
    for i in range(0, nonLinearTrans.length):
        expanded[i] = expanded[i] - nonLinearTrans.normMean[i]
        expanded[i] = expanded[i] / nonLinearTrans.normVar[i]
        
    expanded[nonLinearTrans.length - 1] = 100
    return expanded

# this is a function is called for the elastic alginment portion
def multiply(beta, featureVector):
    result = np.zeros(2)
    
    if (len(beta) != len(featureVector)):
        return np.zeros(2)
        
    for i in range(0, len(featureVector)):
        result[0] = result[0] + featureVector[i] * beta[i][0]
        result[1] = result[1] + featureVector[i] * beta[i][1]
        
    return result

# function to apply given nonlinear transform to a x,y coordinate    
def Apply(location, nonLinearTrans):  
    position = np.array([location[0], location[1]])
    featureVector = kernelExpand(position, nonLinearTrans)
    return multiply(nonLinearTrans.beta, featureVector)
    
def applyInPlace(location, nonLinearTrans):  
    position = np.array([location[0], location[1]])
    featureVector = kernelExpand(position, nonLinearTrans)
    location = multiply(nonLinearTrans.beta, featureVector)
    return location

# define realtile object
class realPatchInfo(object):
    def __init__(self, zLayer, patchName, imagePath, width, height, 
                 transformedPoint):
        self.zLayer = zLayer
        self.patchName = patchName
        self.imagePath = imagePath 
        self.width = width
        self.height = height 
        #minX,minY are the upper lefthand corner of the tile
        self.transformedPoint = transformedPoint 
        self.xMin = int(self.transformedPoint[0] - self.width)
        self.xMax = int(self.transformedPoint[0])
        self.yMin = int(self.transformedPoint[1] - self.height)
        self.yMax = int(self.transformedPoint[1])

# define pseudotile object
class pseudoTileInfo(object):
    def __init__(self, zLayer, patchName, imagePath, o_width, o_height, col, 
                 row, shiftToRealCoords):
        self.zLayer = zLayer
        self.patchName = patchName
        self.imagePath = imagePath
        self.o_width = o_width
        self.o_height = o_height
        self.col = col
        self.row = row
        self.shiftToRealCoords = shiftToRealCoords
        self.overlap = 500.0
        self.xMin = self.col * int(self.o_width - self.overlap) + \
                    shiftToRealCoords[0]
        self.xMax = self.col * int(self.o_width - self.overlap) + \
                    int(self.o_width) + shiftToRealCoords[0]
        self.yMin = self.row * int(self.o_height - self.overlap) + \
                    shiftToRealCoords[1]
        self.yMax = self.row * int(self.o_height - self.overlap) + \
                    int(self.o_height) + shiftToRealCoords[1]

# define nonlinear transform object                   
class nonlinearTransform(object):
    def __init__(self, name, dataString):
        self.name = name
        self.dataString = dataString
        fields = filter(None, dataString.split(" "))
        self.dimension = int(fields[0])
        self.length = int(fields[1])
        self.width = int(fields[-2])
        self.height = int(fields[-1])
        self.beta = np.zeros((self.length, 2))
        self.normMean = np.zeros((self.length))
        self.normVar = np.zeros((self.length))
        # shifted because of elements of beta corresponding to fields[2: -2]
        c = 2 
        for i in range(0, self.length): 
            self.beta[i][0] = float(fields[c])
            c += 1
            self.beta[i][1] = float(fields[c])
            c += 1
        for i in range(0, self.length): 
            self.normMean[i] = float(fields[c])
            c += 1        
        for i in range(0, self.length): 
            self.normVar[i] = float(fields[c])
            c += 1                    
            
# define affine transform object                               
class affineTransform(object):
    def __init__(self, name, dataString):
        self.name = name
        self.dataString = dataString
        fields = dataString.split("(")[1].split(")")[0].split(",")
        self.matrix = np.zeros((2,3))
        self.matrix[0][0] = fields[0]
        self.matrix[1][0] = fields[1]
        self.matrix[0][1] = fields[2]
        self.matrix[1][1] = fields[3]
        self.matrix[0][2] = fields[4]
        self.matrix[1][2] = fields[5]

# function to apply given affine transform to a x,y coordinate        
def applyAffine(point, affineMatrix):
    transformedPoint = np.zeros(2)
    if (len(point) != 2 ):
        print "point was not of correct dimensions"
        return transformedPoint
    transformedPoint[0] = (point[0] * affineMatrix[0][0] + point[1] * 
                            affineMatrix[0][1] + affineMatrix[0][2])
    transformedPoint[1] = (point[0] * affineMatrix[1][0] + point[1] * 
                            affineMatrix[1][1] + affineMatrix[1][2])
    return transformedPoint
            
def main():
    # define the files to be accessed names, and the name of output file 
    maskFile = "mask.nii.gz"
    rigidFilename = "rigid_manual.xml"
    elasticFilename = "elastic_aligned.xml"
    mapFileName = "pseudoToReal.json"
    
    # apply mask-created translation of coordinates of pseudotiles with 
    #respect to realtiles
    ratio = 20
    # function returns xMin, yMin from the bounding box around mask
    shiftToRealCoords = getShiftToRealCoordSpace(maskFile) 
    shiftToRealCoords = ratio * shiftToRealCoords[0], ratio * \
                        shiftToRealCoords[1]

    # apply to realtiles TrakEM transformations, use dictionary as data struct 
    #with z layer as key. Make dictionary of list of realtiles with zLayers as keys
    realTileTree = ET.parse(rigidFilename)
    realTileRoot = realTileTree.getroot()
    realTilesInZLayer = {}
    
    for t2Layer in realTileRoot.iter('t2_layer'):
        z = t2Layer.get('z')
        realTilesList = []
        # iterate over t2_patch to populate tile information and data
        for t2Patch in t2Layer.iter('t2_patch'): 
            width = float(t2Patch.get('width'))
            height =  float(t2Patch.get('height'))
            # get the affine transformation matrix
            myAffine = affineTransform("transform", t2Patch.get('transform'))
                        
            # get the identifying title and file path 
            tileName =  t2Patch.get('title')    
            imagePath = t2Patch.get('file_path')

            # get the nonlinear transform matrix and put it into data structure
            for nonLinearTransform in t2Patch.iter('ict_transform'):
                myNonLinear = nonlinearTransform(
                    "lenscorrection.NonLinearTransform", 
                    nonLinearTransform.get('data'))
            
            # apply nonlinear transform on the point (0,0)
            myPoint = Apply((0,0), myNonLinear)
            # apply affine transform on the point after nonlinear transform
            myNewPoint = applyAffine(myPoint, myAffine.matrix)
            # subtract the width and height from the resultant point to match TrakEM
            myFinalPoint = (myNewPoint[0] - float(width)), (myNewPoint[1] - 
                            float(height))
            # append the results to file patchName, width, height, minX, minY
            myRealPatch = realPatchInfo(z, tileName, imagePath, width, height, 
                                        myFinalPoint)
            realTilesList.append(myRealPatch)
        realTilesInZLayer[z] = realTilesList 
               
    # map the pseduo tiles to a TrakEM space, use dictionary as data struct 
    #with z layer as key.  This is essentially recreating their location in 
    #realTile space, prior to mask and minimal bounding box application
    pseudoTileTree = ET.parse(elasticFilename)
    pseudoTileRoot = pseudoTileTree.getroot()
    pseudoTilesInZLayer = {}    
    
    for t2Layer in pseudoTileRoot.iter('t2_layer'):
        z = t2Layer.get('z')
        pseudoTilesList = []
        # iterate over t2_patch to populate tile information and data
        for t2Patch in t2Layer.iter('t2_patch'): 
            # need the old width and old height of pTile for determining bounds in realTile space
            o_width = float(t2Patch.get('o_width'))
            o_height =  float(t2Patch.get('o_height'))
                        
            # get the identifying title and file path 
            tileName =  t2Patch.get('title')    
            imagePath = t2Patch.get('file_path')
            row = int((tileName.split("_")[1]).split(".")[0])
            col = int((tileName.split("_")[2]).split(".")[0])
            
            # append the results to file patchName, width, height, minX, minY
            myPseudoTile = pseudoTileInfo(z, tileName, imagePath, o_width, o_height, col, row, shiftToRealCoords)
            pseudoTilesList.append(myPseudoTile)
        pseudoTilesInZLayer[z] = pseudoTilesList
               
    # iterate over the keys of the pseudoTilesInZLayer
    #note: dict sorted because it doesn't compare all key values of 
    #dictionaries well, otherwise skipping layers
    realTilesInPseudoTilesInZLayer = {}
    for zLayer in sorted(pseudoTilesInZLayer): 
        # make sure that the same key exists in realTilesInZLayer dict
        if (zLayer in realTilesInZLayer):
            pseudoTilesInLayer = {}
            for pseudoTile in pseudoTilesInZLayer[zLayer]:
                rTsInPT = []
                for realTile in realTilesInZLayer[zLayer]:
                    if realTileInPseudoTile(realTile, pseudoTile):
                        rTsInPT.append(realTile.patchName)
                pseudoTilesInLayer[pseudoTile.patchName] = rTsInPT
            realTilesInPseudoTilesInZLayer[zLayer] = pseudoTilesInLayer

    # write to file with pseudotiles contain which realtiles for each zLayer
    with open(mapFileName, 'w') as f:
        json.dump(realTilesInPseudoTilesInZLayer, f)
    
main()