#!/usr/bin/env python

import os, glob, shutil, fnmatch, math, re, numpy, matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from PIL import Image
from matplotlib.path import Path

#Define Output File Name
outputFile="/study/midusref/DATA/Eyetracking/AOISummary.csv"
aoiDir='/study/reference/public/IAPS/IAPS/IAPS_2008_1-20_800x600BMP/IAPS_2008_AOIs/'
imgDir='/study/midus/IAPS2005png/'

COLORORDER=['red','yellow','blue','purple','green','orange','aqua','magenta','pink','tan','indigo','brown']
HATCHORDER=["x","-","|","+","-",".","x","-","|","+","-","."]

#A wrapper function to check if a string is a number (and account for negatives)
def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False
		
CODES = [Path.MOVETO,
			Path.LINETO,
			Path.LINETO,
			Path.LINETO,
			Path.CLOSEPOLY,
			]

#Function to return all matching AOI files and their coordinates.
def getCoordinates(picturename):
	#Load one current image
	aoiNameGroupList = []
	for file in os.listdir(aoiDir):
		if fnmatch.fnmatch(file, "{0}*".format(pictureName)):
			aoiNameGroupList.append(file)
	print("The names of the AOI files are: {0}".format(aoiNameGroupList))
	aoiGroupList = []
	#Get the values and put them in a list called aoiGroupList
	for aoiName in aoiNameGroupList:
		with open("{0}/{1}" .format(aoiDir, aoiName)) as currentFileName:
			stringContent = currentFileName.readlines()
			currentSubList = []
			for string in stringContent:
				dirtyContent = re.split(", |  |=", string)
				content = map(int, [ x for x in dirtyContent if RepresentsInt(x) ])
				if content:
					currentSubList.append(content)
			aoiGroupList.append(currentSubList)
	bad = [0]
	#Remove any empty AOI slots.
	for aoiFile in aoiGroupList:
		while aoiFile.count(bad) > 0:
			aoiFile.remove(bad)
	#print(aoiGroupList)
	numAOIList = []
	for file in aoiGroupList:
		numAOIList.append(len(aoiGroupList[aoiGroupList.index(file)]))
	return aoiGroupList

#Function to Display all the AOIs in Different Colors
def displayAOI(pictureName, aoiAxes, imgDim):
	#Generate the AOI rectangles
	print("Displaying AOIs for picture {0}".format(pictureName))
	aoiGroupList=getCoordinates(pictureName)
	#print(aoiGroupList)
	fileIndex=0
	for aoifile in aoiGroupList:
		for aoi in aoifile:
			usecolor=COLORORDER[fileIndex]
			usehatch=HATCHORDER[fileIndex]
			layer=10-fileIndex
			#print(aoi[1:5])
			if aoi[0] == 1:
				drawOneRect(aoiAxes, aoi[1:5], usecolor, usehatch, imgDim, layer)
			else:
				drawOneEllipse(aoiAxes, aoi[1:5], usecolor, usehatch, imgDim, layer)
		fileIndex=fileIndex+1
		
#Function to Display the Picture as a background
def drawImg(img, anAxes, imgDim):
	#Draw one rectangle on the figure given
	print("Drawing the image")
	anAxes.imshow(img, interpolation="bicubic")
	#anAxes.imshow(img, origin='lower', interpolation="bicubic")

def drawOneEllipse(anAxes, aoi, ellipsecolor, usehatch, imgDim, order):
	#Draw one ellipse on the figure given
	print("Ellipse centered at [{0}, {1}] in {2}".format(aoi[0], aoi[1], ellipsecolor))
	cx=aoi[0]
	cy=imgDim[0]-aoi[1]
	w=2*aoi[2]
	h=2*aoi[3]
	imgArea=imgDim[0]*imgDim[1]
	if 3.1415*aoi[2]*aoi[3] >= imgArea*0.9 :
		print("     Ellipse covers whole image, not presenting. Note, this is likely an error!")
	else:
		opacity = .8
		patch = patches.Ellipse(xy=[cx, cy], height=h, width=w, facecolor="None", hatch=usehatch, edgecolor=ellipsecolor, alpha=opacity, lw=2, antialiased="True", zorder=order)
		anAxes.add_patch(patch)
	
def drawOneRect(anAxes, aoi, rectcolor, usehatch, imgDim, order):
	#Draw one rectangle on the figure given
	print("Rectangle with Coordinates {0} in {1}".format(aoi, rectcolor))
	TopY=imgDim[0]-aoi[3]
	BottomY=imgDim[0]-aoi[1]
	LeftX=aoi[0]
	RightX=aoi[2]
	print("     Top:{0}, Bottom:{1}, Left:{2}, Right: {3}".format(TopY, BottomY, LeftX, RightX))
	verts = [
	(LeftX, BottomY), # left, bottom
	(LeftX, TopY), # left, top
	(RightX, TopY), # right, top
	(RightX, BottomY), # right, bottom
	(0., 0.), # ignored
	]
	imgArea=imgDim[0]*imgDim[1]
	if abs((RightX-LeftX)*(TopY-BottomY)) >= imgArea*0.9 :
		print("     Rectangle represents whole image, not presenting.")
	else:
		opacity = .8
		path = Path(verts, CODES)
		patch = patches.PathPatch(path, facecolor="None", hatch=usehatch, edgecolor=rectcolor, alpha=opacity, lw=2, antialiased="True", zorder=order)
		anAxes.add_patch(patch)
	

#Function to Display the Picture as a backdrop for the AOIs
def getPicture(pictureName, thefigure):
	#Generate the Image over which to display the AOIs
	print("Retrieving Picture {0}".format(pictureName))
	picturePath = "{0}{1}.png".format(imgDir, pictureName)
	img=mpimg.imread(picturePath)
	#img = numpy.array(img).astype(numpy.float) / 255
	return img
	

#Prompt for the Image Identifier
mainLoop="True"
while mainLoop == "True":
  print('To Exit, Enter "exit"')
  pictureName = raw_input('Enter the Image Number: ')
  if pictureName == "exit":
      mainLoop="False"
  else:
  	fig = plt.figure()
	img = getPicture(pictureName, fig)
	imgDim = img.shape
	xSize = imgDim[1]
	ySize = imgDim[0]
	imgAxes = fig.add_axes([0,0,1,1], xlim=[0,xSize], ylim=[0,ySize], axisbg='black', aspect='equal')
	aoiAxes = fig.add_axes([0,0,1,1], xlim=[0,xSize], ylim=[0,ySize], axisbg='None', aspect='equal')
	drawImg(img, imgAxes, imgDim)
	displayAOI(pictureName, aoiAxes, imgDim)
	plt.axis('off')
	fig.canvas.set_window_title(pictureName) 
	plt.show()
	print("######################")
