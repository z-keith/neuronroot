# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       config.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Stores global variables relating to the original image file
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Change this to swap between test images for testing purposes
current_file = 0

# filename stub (the date and sample)
# used for opening an image and naming files made from it
file_name = ""

# location of the initial seed point for tracing
seedYX = (0, 0)

# size of a pixel
cm_per_pixel = 0

# height to scale images to
image_scaled_height = 2000

# minimum size of a tree to be considered not-noise
minimum_tree_size = 0.15 * image_scaled_height

# contains pair of (y,x) tuples representing the printable rectangle of the image
area_whitelist = None

# contains pairs of (y,x) tuples representing the non-printable regions within the whitelist region
area_blacklist = []

margin_ratio = 0.015

# toggle to store whether the user wants to find nodules
search_for_nodules = True


def initialize():
    """
    Sets the global variables for filename and seed point location
    """

    global file_name
    global seedYX
    global cm_per_pixel
    global area_whitelist
    global area_blacklist

    if current_file == 293:
        multiplier = image_scaled_height/8871
        file_name = "2014-06-24-Tri-293"
        seedYX = (int(330*multiplier), int(4578*multiplier))
        cm_per_pixel = 1/(470*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 329:
        multiplier = image_scaled_height/8032
        file_name = "2014-06-26-Tri-329"
        seedYX = (int(1729*multiplier), int(3613*multiplier))
        cm_per_pixel = 1/(465*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 426:
        multiplier = image_scaled_height/7172
        file_name = "2014-08-14-Tri-426"
        seedYX = (int(1393*multiplier), int(6674*multiplier))
        cm_per_pixel = 1/(471*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 427:
        multiplier = image_scaled_height/14344
        file_name = "2014-08-14-Tri-427"
        seedYX = (int(4578*multiplier), int(13346*multiplier))
        cm_per_pixel = 1/(935*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 428:
        multiplier = image_scaled_height/9914
        file_name = "2014-08-14-Tri-428"
        seedYX = (int(5697*multiplier), int(6513*multiplier))
        cm_per_pixel = 1/(470*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]


