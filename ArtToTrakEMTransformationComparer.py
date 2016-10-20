# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 11:52:21 2016

@author: ariaj
"""
import numpy as np
import math
from matplotlib.pyplot import cm
import matplotlib.pyplot as plt

fileName = "distorted_to_undistorted_70799206_0_0"
fileNumber = "70799206"
numberOfXPoints = 16
numberOfYPoints = 16
totalNumOfPoints = numberOfXPoints * numberOfYPoints 
datumPerPoint = 5 #have each point be x1, y1, x2, y2, magnitude
sizeOfDistortionDataMatrix = (totalNumOfPoints, datumPerPoint)
lineNo = 0

#read Art's file and extract data to numpy array, x1,y1, x2,y2 (4 x 16^2 array)
artDistortion = np.zeros(sizeOfDistortionDataMatrix)
ArtFile = open((fileName + ".svg"))
artLine = ArtFile.readline()

matrixSize = (numberOfXPoints, numberOfYPoints)
artX2 = np.zeros(matrixSize)
artY2 = np.zeros(matrixSize)
artMag = np.zeros(matrixSize)

while artLine:
    if 'x1' in artLine:
        stuff = artLine.split("=\'")
        x1 = float(stuff[1].split("\' ")[0])
        y1 = float(stuff[2].split("\' ")[0])
        rowNo = lineNo % 16
        colNo = int (lineNo / 16)
        artX2[rowNo][colNo] = -float(stuff[3].split("\' ")[0]) + x1 #x1 - stuff
        artY2[rowNo][colNo] = float(stuff[4].split("\' ")[0]) - y1 # stuff -y1
        artMag[rowNo][colNo] = math.sqrt((artX2[rowNo][colNo])**2 + (artY2[rowNo][colNo])**2)
        print "x1 : %f  x2:  %f  y1: %f  y2: %f  artMag[][]: %f" , (x1, artX2[rowNo][colNo], y1, artY2[rowNo][colNo], artMag[rowNo][colNo])
        #print "artMag[][]: %f" , artMag[rowNo][colNo]
        lineNo += 1
    artLine = ArtFile.readline()
ArtFile.close()

#read TrakEM produced file and extract data to numpy array, x1,y1, x2,y2 
#make a (16^2 x 4 array)
differenceData = 3 #for delta x, delta y, delta mag
sizeOfDifferences = (numberOfXPoints*numberOfYPoints, differenceData)
differenceInDistortion = np.zeros(sizeOfDifferences)

difMatrixSize = (numberOfXPoints, numberOfYPoints)
differenceX = np.zeros(difMatrixSize)
differenceY = np.zeros(difMatrixSize)
differenceMag = np.zeros(difMatrixSize)

trakDistSize = (numberOfXPoints, numberOfYPoints)
trakX2 = np.zeros(trakDistSize)
trakY2 = np.zeros(trakDistSize)
trakMag = np.zeros(trakDistSize)

lineNo = 0
trakDistortion = np.zeros(sizeOfDistortionDataMatrix)
trakEMFile = open('distortedToUndistortedTrakEM.txt')
trakLine = trakEMFile.readline()

while trakLine:
    if 'x1' in trakLine:
        stuff = trakLine.split(" ")
        rowNo = lineNo % 16
        colNo = int (lineNo / 16)
        x1 = float(stuff[2])
        y1 = float(stuff[4])
        trakX2[rowNo][colNo] = x1 - float(stuff[6])
        trakY2[rowNo][colNo] = float(stuff[8]) - y1
        #print "trakX2: %f  x1:  %f" , (float(stuff[6]), float(stuff[2]))
        trakMag[rowNo][colNo] = math.sqrt((trakX2[rowNo][colNo])**2 + (trakY2[rowNo][colNo])**2)
        differenceX[rowNo][colNo] = artX2[rowNo][colNo] - trakX2[rowNo][colNo]
        #print " differenceX[rowNo][colNo]: %f", differenceX[rowNo][colNo]
        differenceY[rowNo][colNo] = artY2[rowNo][colNo]- trakY2[rowNo][colNo]
        differenceMag[rowNo][colNo] = artMag[rowNo][colNo] - trakMag[rowNo][colNo]
        lineNo +=1
    trakLine = trakEMFile.readline()
        
trakEMFile.close()

X, Y = np.mgrid[120:3720:16j, 120:3720:16j] #pretty much the same thing as x1,y1

plot = plt.figure()
plt.quiver(X, Y, differenceX, differenceY, 
           differenceMag, cmap=cm.viridis, headlength=5) 
plt.colorbar()
plt.gca().invert_yaxis()
titleString = "Differences Quiver Plot for " + fileNumber
plt.title(titleString)
plt.xlabel("X Position in Pixels")
plt.ylabel("Y Position in Pixels")
pltTitle = 'differenceQuiverPlot' + fileNumber + '.svg'
plot.savefig(pltTitle , format='svg', dpi=3000)
plt.show(plot)


plotTrak = plt.figure()
plt.quiver(X, Y, trakX2, trakY2, 
           trakMag, cmap=cm.viridis, headlength=5) 
plt.colorbar()
plt.gca().invert_yaxis()
titleString = "Trak Quiver Plot for " + fileNumber
plt.title(titleString)
plt.xlabel("X Position in Pixels")
plt.ylabel("Y Position in Pixels")
pltTitle = 'trakQuiverPlot' + fileNumber + '.svg'
plotTrak.savefig(pltTitle, format='svg', dpi=3000)
plt.show(plotTrak)

plotArt = plt.figure()
plt.quiver(X, Y, artX2, artY2, 
           artMag, cmap=cm.viridis, headlength=5) 
plt.colorbar()
plt.gca().invert_yaxis()
titleString = "Art's Quiver Plot for " + fileNumber
plt.title(titleString)
plt.xlabel("X Position in Pixels")
plt.ylabel("Y Position in Pixels")
pltTitle = 'artQuiverPlot' + fileNumber + '.svg'
plotArt.savefig(pltTitle, format='svg', dpi=3000)
plt.show(plotArt)
