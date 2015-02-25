#-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fImageHandlers
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    functions for loading and displaying images and graphs
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
from skimage import data
from matplotlib import pyplot
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
    outimage = np.zeros((ysize, xsize))
    for key in node_dict:
        outimage[node_dict[key].Y, node_dict[key].X] = (255)
    misc.imsave("TestImages/2014-06-24-Tri-293-trace.tif", outimage)
    #misc.imsave("TestImages/2014-06-26-Tri-329-trace.tif", outimage)
