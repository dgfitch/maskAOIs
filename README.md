# maskAOI.py


## About

Written by Dan Fitch, heavily based on work by Andy Schoen in viewAOI.py.

Uses PIL to combine some various saliency toolkits with AOI (area of interest) masks saved in .OBT format, and generate statistics.


## Technical junk

All luminances are weighted as in YUV.

Complexity is the filesize in bytes after saving as a JPG. 
Due to stippling and other image artifacts in some of the files,
I would NOT rely too much on this number.


## Output

Given a directory, assuming there are matching OBT and saliency masks,
this script generates a CSV containing:

    1. original image: luminance
    2. original image: mean red, green, and blue values
    3. original image: complexity 
    4. AOI: (0 is all shapes in the OBT file, minus "entire file" shapes, E is all shapes 2 and greater if there are any, 1-4 are the individual masks in the order they are in the OBT, for each of these things we give:)
        A. `mask_lum`: luminance of mask
        B. `in_lum`: luminance of original image INSIDE mask
        C. `out_lum`: luminance of original image OUTSIDE mask
        D. `in_r`, `in_g`, `in_b`: RGB means for original image INSIDE mask
        E. `in_complexity`: complexity INSIDE mask
        F. `out_r`, `out_g`, `out_b`: RGB means for original image OUTSIDE mask
        G. `out_complexity`: complexity OUTSIDE mask
    5. Saliency luminance
    6. Saliency AOI dotproduct sum
    7. Saliency: (As with AOI, 0 is all shapes in the OBT file, E is shapes 2 and greater in the OBT file, 1-4 are individual masks)
        A. `in_lum`: luminance of saliency map INSIDE mask
        B. `out_lum`: luminance of saliency map OUTSIDE mask
    8. SunSaliency luminance
    9. SunSaliency AOI dotproduct sum
    10. SunSaliency: (As with AOI, 0 is all shapes in the OBT file, E is shapes 2 and greater in the OBT file, 1-4 are individual masks)
        A. `in_lum`: luminance of SUN saliency map INSIDE mask
        B. `out_lum`: luminance of SUN saliency map OUTSIDE mask

