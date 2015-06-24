# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       Config
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Image initialization (will allow for sequential loading of images and user-selected seed points and
#               pixel scales via a clickable window)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Change this to swap between test images for testing purposes (currently supports 2, 293, 2930, and 329)
current_file = 2

# filename stub (the date and sample)
# used for opening an image and naming files made from it
filename = ""

# location of the initial seed point for tracing
seedX = 0
seedY = 0

# height to scale images to
image_scaled_height = 4000

# minimum size of a tree to be considered not-noise
minimum_tree_size = 1000


def init():
    """
    Sets the global variables for filename and seed point location
    """
    # TODO: implement seed point and scale selection window

    global filename
    global seedX
    global seedY

    if current_file == 2:
        filename = "2015-04-22-Pai-002"
        seedX = 233
        seedY = 92

    if current_file == 293:
        filename = "2014-06-24-Tri-293"
        seedX = 1035
        seedY = 74

    if current_file == 2930:
        filename = "2014-06-24-Tri-293-ORIGINAL"
        seedX = 2070
        seedY = 148

    if current_file == 329:
        filename = "2014-06-26-Tri-329"
        seedX = 901
        seedY = 432
