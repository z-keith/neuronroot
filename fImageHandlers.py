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
        if not node_dict[key].Removed:
            outarray[node_dict[key].Y, node_dict[key].X] = 0xFFFFFFFF

    outarray = RecursivePrint(node_dict, set([config.best_node]), outarray)

    # save image
    outimage = Image.fromarray(outarray, 'RGBA')
    outimage.save('TestImages/{0}-skeleton.tif'.format(config.filename))


def RecursivePrint(node_dict, current_set, outarray):
    while True:
        next_set = set()

        for key in current_set:
            if not node_dict[key].Printed:
                outarray[node_dict[key].Y, node_dict[key].X] = [config.red, config.green, config.blue, 255]
                for child_key in node_dict[key].Children:
                    if not node_dict[child_key].Removed:
                        next_set.add(child_key)
                node_dict[key].Printed = True

        if len(next_set) > 0:
            if config.redAscending:
                config.red += 1
                if config.red > 230:
                    config.redAscending = False
            else:
                config.red -=1
                if config.red < 60:
                    config.redAscending = True

            if config.blueAscending:
                config.blue += 2
                if config.blue > 230:
                    config.blueAscending = False
            else:
                config.blue -=2
                if config.blue < 60:
                    config.blueAscending = True

            if config.greenAscending:
                config.green += 3
                if config.green > 230:
                    config.greenAscending = False
            else:
                config.green -=3
                if config.green < 60:
                    config.greenAscending = True

            current_set = next_set

        else:
            return outarray

def ColorArea(node_dict, key, outarray):

    # need to find a new way to color within the radius, since the nodes that are covered have been removed

    return outarray
