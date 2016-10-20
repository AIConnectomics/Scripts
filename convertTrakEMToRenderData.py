# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 15:18:13 2016

@author: ariaj
"""
import json
import xml.etree.ElementTree as ET

class transform(object):
    def __init__(self, tileType, className, dataString):
        self.tileType = tileType
        self.className = className
        self.dataString = dataString
            
    def convertToString(self):
        stringForm = 'type : ' + self.tileType + ', className : ' + self.className + ', '
        stringForm += 'dataString : ' + self.dataString
        return stringForm
        
    def convertToDict(self):
        dictionary = {'type': self.tileType, 'className' : self.className, 'dataString' : self.dataString}
        return dictionary
            
class tileSpec(object):
    def __init__(self, title, imageUrl, maskUrl):
        self.title = title
        self.imageUrl = imageUrl
        self.maskUrl = maskUrl
        self.specList = []        
        
    def assignTransforms(self, listOfTransforms):
        for transform in listOfTransforms:
            self.specList.append(transform)
        
    def convertToString(self):
        stringForm = '{ tileId : ' + self.title.split('.')[0] + ', '
        stringForm += 'mipmapLevels : { 0 : { imageUrl : ' + self.imageUrl 
        stringForm += ', maskUrl  : ' + self.maskUrl + '}},'
        stringForm += 'transforms : { type : list, specList : ['
        for transform in self.specList:
            stringForm += '{' + transform.convertToString() + '}'
            if transform != self.specList[-1]:
                stringForm += ', '
        stringForm += '] } }'
        return stringForm
        
    def convertToDict(self):
        #transforms dictionary generation
        specListOfDict = []
        for transform in self.specList:
            specListOfDict.append(transform.convertToDict())
        transformsDict = {'type' : 'list', 'specList' : specListOfDict}
        mipmapDict = { '0' : { 'imageUrl' : self.imageUrl, 'maskUrl' : self.maskUrl}}
        dictionary = {'tileId' : self.title.split('.')[0], 'mipmapLevels' : mipmapDict, 'transforms' : transformsDict}
        return dictionary
    
#process strings from xml file for render-like string
def getJustTheMatrix(matrixString):
    justEntries = matrixString.split("(")[1].split(")")[0]
    justEntries = justEntries.split(",")
    justEntries = ' '.join(justEntries)
    return justEntries
  
#in main open and read rigid_align and make a data structure for that data chunk
def main():
    renderFilename = "myRenderable.json"
    readFilename = "rigid_manual.xml"
    maskUrl = "outputmask.png"
    lensCo = ''    
    tileSpecs = []
    
    tree = ET.parse(readFilename)
    root = tree.getroot()
    
    #find x, y, width, height, and scale and other higher level stuff
    for t2layerSet in root.iter('t2_layer_set'):
        #get the identity matrix that's in the file for porting to render-able
        identityTransformString = t2layerSet.get('transform')
        identityMatrix = getJustTheMatrix(identityTransformString)

    defaultTransform = transform('leaf', 'mpicbg.trakem2.transform.AffineModel2D', identityMatrix)
    
    #iterate over t2_patch to populate tile information and data
    for t2Patch in root.iter('t2_patch'): 
        #get the affine transform matrix and put it into data structure
        affineTransformMatrix = getJustTheMatrix(t2Patch.get('transform')) 
        affineTransform = transform('leaf', 'mpicbg.trakem2.transform.AffineModel2D', affineTransformMatrix)
        
        #get the identifying title and file path 
        title = t2Patch.get('title')
        imageUrl = t2Patch.get('file_path')

        #get the nonlinear transform matrix and put it into data structure
        for ictTransform in t2Patch.iter('ict_transform'):
            className = ictTransform.get('class')
            lensCo = ictTransform.get('data') 
        nonLinearTransform = transform('leaf', className, lensCo)

        #generate the current informations tile specs as a dictionary
        listOfTransforms=[affineTransform, nonLinearTransform, defaultTransform]
        currentSpec = tileSpec(title, imageUrl, maskUrl)
        currentSpec.assignTransforms(listOfTransforms)
        tileSpecs.append(currentSpec.convertToDict())
    
    #make all the tile spec information a json file
    renderDict = {'tileSpecs' : tileSpecs}
    with open(renderFilename, 'w') as f:
        json.dump(renderDict, f)
    
main()