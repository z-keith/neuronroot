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
import numpy as np

# Function import declarations

def LoadImage(Filepath):
    ImgArray = data.imread(Filepath, as_grey=True)
    return ImgArray
    
def PrepImage(ImgArray):
    globalThreshold = 0.8*ImgArray.mean()
    ImgArray[ImgArray<globalThreshold] = 0
    # consider a wider area for the median filter in larger images
    ImgArray = ndimage.filters.median_filter(ImgArray, size=(5,5))
    return ImgArray
    
def PrintImage(ImgArray):
    pyplot.figure(figsize=(3, 3))
    pyplot.axes([0, 0, 1, 1])
    pyplot.imshow(ImgArray, cmap=pyplot.cm.gray)
    pyplot.axis('off')
    pyplot.show()

def PrintRepresentation(node_dict, xsize, ysize):
    outimage = np.zeros((ysize, xsize))
    for key in node_dict:
        outimage[node_dict[key].Y, node_dict[key].X] = (255)
    #misc.imsave("TestImages/2014-06-24-Tri-293-trace.gif", outimage)
    misc.imsave("TestImages/2014-06-26-Tri-329-trace.gif", outimage)
