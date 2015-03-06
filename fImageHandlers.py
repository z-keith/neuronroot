#-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fImageHandlers
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    functions for loading and displaying images and graphs
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
from scipy import ndimage, misc
from PIL import Image
import numpy as np
import config

# Class import declarations

# Function import declarations

def LoadImage(Filepath):
    Img = Image.open(Filepath)

    baseheight = 2000
    wpercent = (baseheight/float(Img.size[1]))
    wsize = int((float(Img.size[0])*float(wpercent)))
    Img = Img.resize((wsize, baseheight))

    ImgArray = np.array(Img)
    ImgArray = np.dot(ImgArray[...,:3], [0.299, 0.587, 0.144])
    ImgArray = PrepImage(ImgArray)

    print("Completed load and threshold in " + config.PrintTimeBenchmark())

    return ImgArray
    
def PrepImage(ImgArray):
    globalThreshold = ImgArray.mean() * 0.8
    ImgArray[ImgArray<globalThreshold] = 0
    ImgArray = ndimage.filters.median_filter(ImgArray, size=(5,5))
    return ImgArray

def PrintRepresentation(node_dict):
    outarray =np.zeros((config.sizeY, config.sizeX),np.uint32)
    for i in range(config.sizeX):
        for j in range(config.sizeY):
            outarray[j][i] = 0xFF000000
    for key in node_dict:
        outarray[node_dict[key].Y, node_dict[key].X] = 0xFFFFFFFF
    outimage = Image.fromarray(outarray, 'RGBA')
    outimage.save("TestImages/" + config.filename + "-trace.tif")

