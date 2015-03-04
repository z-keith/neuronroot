#-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fImageHandlers
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    functions for loading and displaying images and graphs
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import os
from scipy import ndimage, misc
from PIL import Image
import numpy as np

# Function import declarations

def LoadImage(Filepath):
    Img = Image.open(Filepath)

    baseheight = 2000
    wpercent = (baseheight/float(Img.size[1]))
    wsize = int((float(Img.size[0])*float(wpercent)))
    Img = Img.resize((wsize, baseheight))

    ImgArray = np.array(Img)
    ImgArray = np.dot(ImgArray[...,:3], [0.299, 0.587, 0.144])
    return ImgArray
    
def PrepImage(ImgArray):
    globalThreshold = ImgArray.mean() * 0.8
    ImgArray[ImgArray<globalThreshold] = 0
    ImgArray = ndimage.filters.median_filter(ImgArray, size=(5,5))
    return ImgArray

def PrintRepresentation(node_dict, xsize, ysize):
    outarray =np.zeros((ysize, xsize),np.uint32)
    for i in range(xsize):
        for j in range(ysize):
            outarray[j][i] = 0xFF000000
    for key in node_dict:
        outarray[node_dict[key].Y, node_dict[key].X] = 0xFF00FF00
    outimage = Image.fromarray(outarray, 'RGBA')
    outimage.save("TestImages/" + os.environ["FILENAME"] + "-trace.tif")

