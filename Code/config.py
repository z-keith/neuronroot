# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       config.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Stores global variables relating to the original image file
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Change this to swap between test images for testing purposes (currently supports 2, 293, 2930, and 329)
current_file = 293

# filename stub (the date and sample)
# used for opening an image and naming files made from it
file_name = ""

# location of the initial seed point for tracing
seedYX = (0, 0)

# size of a
cm_per_pixel = 0

# height to scale images to
image_scaled_height = 6000

# minimum size of a tree to be considered not-noise
minimum_tree_size = 0.25 * image_scaled_height


def initialize():
    """
    Sets the global variables for filename and seed point location
    """
    # TODO: implement seed point and scale selection window

    global file_name
    global seedYX
    global cm_per_pixel

    if current_file == 2:
        file_name = "2015-04-22-Pai-002"
        seedYX = (92, 233)
        cm_per_pixel = 1

    if current_file == 293:
        file_name = "2014-06-24-Tri-293"
        seedYX = (74, 1035)
        cm_per_pixel = 1/105

    if current_file == 2930:
        file_name = "2014-06-24-Tri-293-ORIGINAL"
        seedYX = (148, 2070)
        cm_per_pixel = 1/1050

    if current_file == 329:
        file_name = "2014-06-26-Tri-329"
        seedYX = (432, 901)
        cm_per_pixel = 1/115
