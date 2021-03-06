#!/usr/bin/env python

"""
maskAOI.py

Dan Fitch 20150618
"""

from __future__ import print_function

import sys, os, glob, shutil, fnmatch, math, re, numpy, csv
from PIL import Image, ImageFile, ImageDraw, ImageColor, ImageOps, ImageStat
ImageFile.MAXBLOCK = 1048576

DEBUG = False

AOI_DIR='/study/reference/public/IAPS/IAPS/IAPS_2008_1-20_800x600BMP/IAPS_2008_AOIs/'
IMG_DIR='/study/midus/IAPS2005png/'
SALIENCY_DIR='/home/fitch/aoi/saliency/'
SUN_SALIENCY_DIR='/home/fitch/aoi/sunsaliency/'
MASK_NAMES = ["0", "E", "1", "2", "3", "4"]


# A wrapper function to check if a string is a number (and account for negatives)
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


def drawAOI(aoi, i, d):
    if aoi[0] == 1:
        drawOneRect(aoi[1:5], i, d)
    else:
        drawOneEllipse(aoi[1:5], i, d)

# Function to display the AOI as masks
def createAOIMasks(pictureName, size):
    if DEBUG: print("Displaying AOIs for picture {0}".format(pictureName))
    aoiList = getCoordinates(pictureName)

    if aoiList == []: return None

    masks = []

    # L is grayscale
    img = Image.new("L", size, 0)
    draw = ImageDraw.Draw(img)

    for aoi in aoiList:
        drawAOI(aoi, img, draw)

    masks.append(img)

    # Now the "emotional" masks, index 2 and up theoretically
    emo = Image.new("L", size, 0)
    emo_draw = ImageDraw.Draw(emo)

    for aoi in aoiList[1:]:
        drawAOI(aoi, emo, emo_draw)

    masks.append(emo)

    # Now we draw each mask individually
    for aoi in aoiList:
        individual = Image.new("L", size, 0)
        individual_draw = ImageDraw.Draw(individual)
        drawAOI(aoi, individual, individual_draw)
        masks.append(individual)

    return masks

		
def drawOneEllipse(aoi, img, draw):
    #Draw one ellipse on the figure given
    if DEBUG: print("Ellipse centered at [{0}, {1}] with {2} {3}".format(aoi[0], aoi[1], aoi[2], aoi[3]))
    imgDim = img.size
    cx=aoi[0]
    cy=aoi[1]
    w=2*aoi[2]
    h=2*aoi[3]
    imgArea=imgDim[0]*imgDim[1]
    LeftX=cx-aoi[2]
    RightX=cx+aoi[2]
    TopY=cy-aoi[3]
    BottomY=cy+aoi[3]
    draw.ellipse(((LeftX,TopY),(RightX,BottomY)), fill="white", outline="white")
	
def drawOneRect(aoi, img, draw):
    #Draw one rectangle on the figure given
    if DEBUG: print("Rectangle with Coordinates {0}".format(aoi))
    imgDim = img.size
    TopY=aoi[3]
    BottomY=aoi[1]
    LeftX=aoi[0]
    RightX=aoi[2]
    if DEBUG: print("     Top:{0}, Bottom:{1}, Left:{2}, Right: {3}".format(TopY, BottomY, LeftX, RightX))
    imgArea=imgDim[0]*imgDim[1]
    draw.rectangle(((LeftX,TopY),(RightX,BottomY)), fill="white", outline="white")

def stat(img, mask=None):
    if mask == None:
        return ImageStat.Stat(img)
    else:
        return ImageStat.Stat(img, mask)

def brightness(img, mask=None):
    return stat(img,mask).rms[0]
	
def luminance(c):
    if len(c) < 3 or len(c) > 4:
        raise Exception("Luminance got values: ", c)
    r = c[0]
    b = c[1]
    g = c[2]
    lum = r*0.2126 + g*0.7152 + b*0.0722
    if len(c) == 4:
        # Multiply by alpha... kind of hokey but should work for most cases
        result = lum * (c[3] / 255.0)
    else:
        result = lum

    if math.isnan(result):
        return 0.0
    else:
        return result

def complexity(pictureName, key, img):
    name = "masks/{0}-{1}.jpg".format(pictureName, key)
    img.save(name, quality=80, format="JPEG", optimize=True, progressive=True)
    size = os.path.getsize(name)
    #os.remove(name)
    return size



def results_for_mask(withColors, original, pictureName, key, mask):
    # We also want the area outside of the mask
    mask_inverted = ImageOps.invert(mask)
    stats_mask = stat(mask)
    stats_in = stat(original, mask)
    stats_out = stat(original, mask_inverted)

    # Complexity uses the resultant image saved as jpg, so we need to prepare some actual images

    stats_in_image = Image.new('RGBA', original.size, "black")
    stats_in_image.paste(original, mask=mask)
    stats_out_image = Image.new('RGBA', original.size, "black")
    stats_out_image.paste(original, mask=mask_inverted)

    try:
        if withColors:
            return {
                key + '_mask_lum': stats_mask.mean[0] / 256.0,
                key + '_in_lum': luminance(stats_in.mean) / 256.0,
                key + '_in_r': stats_in.mean[0] / 256.0,
                key + '_in_g': stats_in.mean[1] / 256.0,
                key + '_in_b': stats_in.mean[2] / 256.0,
                key + '_in_complexity': complexity(pictureName, key + "in", stats_in_image),
                key + '_out_lum': luminance(stats_out.mean) / 256.0,
                key + '_out_r': stats_out.mean[0] / 256.0,
                key + '_out_g': stats_out.mean[1] / 256.0,
                key + '_out_b': stats_out.mean[2] / 256.0,
                key + '_out_complexity': complexity(pictureName, key + "out", stats_out_image),
            }
        else:
            return {
                key + '_in_lum': luminance(stats_in.mean) / 256.0,
                key + '_out_lum': luminance(stats_out.mean) / 256.0,
            }
    except ZeroDivisionError:
        return {}

def do_saliency(original, masks, path, prefix, pictureName, results):
    saliency = Image.open(path + pictureName + ".png")
    if saliency.mode != "RGBA":
        saliency = saliency.convert("RGBA")
    saliency = saliency.resize(original.size)
    stats_saliency = stat(saliency)
    results[prefix + '_lum'] = luminance(stats_saliency.mean) / 256.0

    for i, mask in zip(MASK_NAMES, masks):
        stuff = results_for_mask(False, saliency, pictureName, prefix + i, mask)
        results.update(stuff)

    saliency_bw = saliency.convert("L")
    s_array = numpy.array(saliency_bw)
    m_array = numpy.array(masks[0])
    dot = numpy.dot(s_array, numpy.rot90(m_array))

    results[prefix + "_aoi_dotproduct_sum"] = numpy.sum(dot)


def write_stats(writer, filename, pictureName):

    original = Image.open(IMG_DIR + filename)

    if original.mode != "RGBA":
        # P is palette. Did you know BMP *and* PNG files can have 8-bit palettes? WHAAAT
        original = original.convert("RGBA")

    # First, draw the AOI masks in white on black
    # This returns a list, the first mask is ALL AOIs, the second is the "emotional" ones >=2, and the rest are each individual shape
    masks = createAOIMasks(pictureName, original.size)

    if masks == None:
        print("No masks found in: " + filename)
        return False

    stats_orig = stat(original)

    results = {
        'image_name': pictureName,
        'orig_lum': luminance(stats_orig.mean) / 256.0,
        'orig_r': stats_orig.mean[0] / 256.0,
        'orig_g': stats_orig.mean[1] / 256.0,
        'orig_b': stats_orig.mean[2] / 256.0,
        'orig_complexity': complexity(pictureName, "original", original),
    }

    for i, mask in zip(MASK_NAMES, masks):
        stuff = results_for_mask(True, original, pictureName, 'aoi' + i, mask)
        results.update(stuff)

    # And finally we get the saliency image and resize it and do a bunch of garbage with it and the AOI masks

    do_saliency(original, masks, SALIENCY_DIR, "saliency", pictureName, results)
    do_saliency(original, masks, SUN_SALIENCY_DIR, "sun_saliency", pictureName, results)


    writer.writerow(results)
    if DEBUG: print("Generated stats for " + filename)
    return True



with open('stats.csv', 'wb') as csvfile:
    per_mask_fields = [
        '_mask_lum',
        '_in_lum',
        '_in_r',
        '_in_g',
        '_in_b',
        '_in_complexity',
        '_out_lum',
        '_out_r',
        '_out_g',
        '_out_b',
        '_out_complexity',
    ]

    per_saliency_fields = [
        '_in_lum',
        '_out_lum',
    ]

    fields = [
        'image_name',
        'orig_lum',
        'orig_r',
        'orig_g',
        'orig_b',
        'orig_complexity',
    ]

    for i in MASK_NAMES:
        for f in per_mask_fields:
            fields.append("aoi{0}{1}".format(i,f))

    fields.append("saliency_aoi_dotproduct_sum")
    fields.append("saliency_lum")

    for i in MASK_NAMES:
        for f in per_saliency_fields:
            fields.append("saliency{0}{1}".format(i,f))

    fields.append("sun_saliency_aoi_dotproduct_sum")
    fields.append("sun_saliency_lum")

    for i in MASK_NAMES:
        for f in per_saliency_fields:
            fields.append("sun_saliency{0}{1}".format(i,f))

    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writerow(dict(zip(fields,fields)))

    for filename in sorted(os.listdir(IMG_DIR)):
        if not ".png" in filename:
            continue

        pictureName = filename.replace(".png", "")

        try:
            write_stats(writer, filename, pictureName)

        except:
            print("Error on file " + pictureName, file=sys.stderr)
            raise


