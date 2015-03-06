#-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fImageHandlers
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    functions for loading and displaying images and graphs
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
from scipy import ndimage
from PIL import Image
import numpy
import config


def LoadImage(filepath):
    """
    Main image loading function. Loads, resizes, and filters an image.
    :param filepath: name of image to open
    :return: numpy array of floats 0-255 representing brightness at that location
    """
    img = Image.open(filepath)

    # scale image
    base_height = 2000
    scaling_percent = (base_height/float(img.size[1]))
    scaled_width = int(float(img.size[0])*scaling_percent)
    img = img.resize((scaled_width, base_height))

    # make array from image
    img_array = numpy.array(img)
    # make image black and white
    img_array = numpy.dot(img_array[...,:3], [0.299, 0.587, 0.144])
    img_array = PrepImage(img_array)

    print("Completed load and threshold in {0}".format(config.PrintTimeBenchmark()))

    return img_array


def PrepImage(img_array):
    """
    Threshold and filter an image array
    :param img_array: numpy array of floats 0 - 255 representing brightness at that location
    :return: numpy array of floats 0 - 255 representing brightness at that location
    """
    THRESHOLD_MULTIPLIER = 0.8

    # threshold the image based on the mean brightness of the image
    globalThreshold = img_array.mean() * THRESHOLD_MULTIPLIER
    img_array[img_array<globalThreshold] = 0

    img_array = ndimage.filters.median_filter(img_array, size=(5,5))

    return img_array


def PrintRepresentation(node_dict):
    """
    Prototype function for displaying a visual representation of a node_dict
    :param node_dict: dictionary of the form {int: Node}
    """
    # initialize array
    outarray = numpy.zeros((config.sizeY, config.sizeX), numpy.uint32)

    # set array to black
    for i in range(config.sizeX):
        for j in range(config.sizeY):
            outarray[j][i] = 0xFF000000

    # set all locations containing a node to white
    for key in node_dict:
        outarray[node_dict[key].Y, node_dict[key].X] = 0xFFFFFFFF

    # save image
    outimage = Image.fromarray(outarray, 'RGBA')
    outimage.save("TestImages/{0}-trace.tif".format(config.filename))

