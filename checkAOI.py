#!/usr/bin/env python

"""
analyzeAOI.py

Dan Fitch 20150618

Heavily based on work by Andy Schoen in viewAOI.py

Looks at OBT files and looks for any with ONLY ONE AOI,
or any with no AOIs covering >90%
"""

from __future__ import print_function

import sys, os, glob, shutil, fnmatch, math, re, numpy, csv
from PIL import Image, ImageFile, ImageDraw, ImageColor, ImageOps, ImageStat
ImageFile.MAXBLOCK = 1048576

DEBUG = False

AOI_DIR='/study/reference/public/IAPS/IAPS/IAPS_2008_1-20_800x600BMP/IAPS_2008_AOIs/'
IMG_DIR='/study/midus/IAPS2005png/'


#A wrapper function to check if a string is a number (and account for negatives)
def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False
		

#Function to return only the main, averaged AOI files (the .OBT) and their coordinates.
def getCoordinates(picturename):
    #Load one current image
    aoiName = picturename + ".OBT"
    aoiList = []
    obtfile = "{0}/{1}".format(AOI_DIR, aoiName)
    if not os.path.exists(obtfile):
        if DEBUG: print("WARNING: No OBT file found for " + picturename)
        return []
    with open(obtfile) as file:
        stringContent = file.readlines()
        for string in stringContent:
            dirtyContent = re.split(", |  |=", string)
            content = map(int, [ x for x in dirtyContent if RepresentsInt(x) ])
            if content and content != [0]:
                aoiList.append(content)
    return aoiList


def checkAOI(aoi, size):
    if aoi[0] == 1:
        return checkOneRect(aoi[1:5], size)
    else:
        return checkOneEllipse(aoi[1:5], size)

# Function to display the AOI as masks
def checkAOIMasks(pictureName, size):
    if DEBUG: print("Checking AOIs for picture {0}".format(pictureName))
    aoiList = getCoordinates(pictureName)

    if aoiList == []: return None

    masks = []

    foundLarge = False
    for aoi in aoiList:
        used = checkAOI(aoi, size)
        if not used:
            foundLarge = True

    if len(aoiList) < 2:
        print("Found {0} AOIs in {1}".format(len(aoiList), pictureName))

    if not foundLarge:
        print("Did not find large mask in {0}".format(pictureName))


		
def checkOneEllipse(aoi, size):
    if DEBUG: print("Ellipse centered at [{0}, {1}] with {2} {3}".format(aoi[0], aoi[1], aoi[2], aoi[3]))
    imgDim = size
    cx=aoi[0]
    cy=aoi[1]
    w=2*aoi[2]
    h=2*aoi[3]
    imgArea=imgDim[0]*imgDim[1]
    LeftX=cx-aoi[2]
    RightX=cx+aoi[2]
    TopY=cy-aoi[3]
    BottomY=cy+aoi[3]
    if 3.1415*aoi[2]*aoi[3] >= imgArea*0.9 :
        if DEBUG: print("     Ellipse covers whole image, not presenting. Note, this is likely an error!")
        return False
    else:
        return True
	
def checkOneRect(aoi, size):
    if DEBUG: print("Rectangle with Coordinates {0}".format(aoi))
    imgDim = size
    TopY=aoi[3]
    BottomY=aoi[1]
    LeftX=aoi[0]
    RightX=aoi[2]
    if DEBUG: print("     Top:{0}, Bottom:{1}, Left:{2}, Right: {3}".format(TopY, BottomY, LeftX, RightX))
    imgArea=imgDim[0]*imgDim[1]
    if abs((RightX-LeftX)*(TopY-BottomY)) >= imgArea*0.9 :
        if DEBUG: print("     Rectangle represents whole image, not presenting.")
        return False
    else:
        return True


for filename in sorted(os.listdir(IMG_DIR)):
    if not ".png" in filename:
        continue

    pictureName = filename.replace(".png", "")
    

    try:
        original = Image.open(IMG_DIR + filename)
        checkAOIMasks(pictureName, original.size)

    except:
        print("Error on file " + pictureName, file=sys.stderr)
        raise


