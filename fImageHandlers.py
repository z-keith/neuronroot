#-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fImageHandlers
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    functions for loading and displaying images and graphs
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
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
    scaling_ratio = (base_height/float(img.size[1]))
    if scaling_ratio < 1:
        scaled_width = int(float(img.size[0])*scaling_ratio)
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
    THRESHOLD_MULTIPLIER = 1.0

    # threshold the image based on the mean brightness of the image
    globalThreshold = img_array.mean() * THRESHOLD_MULTIPLIER
    img_array[img_array<globalThreshold] = 0

    #img_array = ndimage.filters.median_filter(img_array, size=(5,5))

    return img_array


def PrintInitial(node_dict):
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

    # set all locations containing a node to grey
    for key in node_dict:

        # Print as grey
        outarray[node_dict[key].Y, node_dict[key].X] = 0xFF222222

    # save image
    outimage = Image.fromarray(outarray, 'RGBA')
    outimage.save('TestImages/{0}-skeleton.tif'.format(config.filename))


def PrintSkeleton(node_dict):
    """
    Prototype function for displaying a visual representation of a node_dict
    :param node_dict: dictionary of the form {int: Node}
    """
    # initialize array
    img = Image.open('TestImages/{0}-skeleton.tif'.format(config.filename))
    outarray = numpy.array(img)

    for key in node_dict:
        if node_dict[key].Radius > 20:
            outarray = ColorArea(node_dict, key, outarray)

    # set all locations containing a node to a color dependent on the radius at the point
    for key in node_dict:

        # Colorized by radius
        # outarray[node_dict[key].Y, node_dict[key].X] = 0xFF888888 + 0x8912 * (0xFF % (4*node_dict[key].Radius + 1))

        # White
        if not node_dict[key].Removed:
            outarray[node_dict[key].Y, node_dict[key].X] = 0xFFFFFFFF

        # branch nodes only
        # if len(node_dict[key].Children) > 1:
            # outarray[node_dict[key].Y, node_dict[key].X] = 0xFFFFFFFF

    # save image
    outimage = Image.fromarray(outarray, 'RGBA')
    outimage.save('TestImages/{0}-skeleton.tif'.format(config.filename))

def ColorArea(node_dict, key, outarray):

    # need to find a new way to color within the radius, since the nodes that are covered have been removed

    return outarray
