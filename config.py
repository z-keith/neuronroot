# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       config.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Stores global variables relating to the original image file
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Change this to swap between test images for testing purposes
# current_file = 293

# filename stub (the date and sample)
# used for opening an image and naming files made from it
file_name = None

# current filepath
infile_path = "../TestImages/"

outfile_path = "../Output/"

# file extension
file_extension = ".tif"
proper_file_extension = ".jpg"

# height to scale images to
image_scaled_height = 2000

# location of the initial seed point for tracing
seedYX = (0,0)

# size of a pixel
cm_per_pixel = 1/(470*image_scaled_height/8871)

# minimum size of a tree to be considered not-noise
minimum_tree_size = 0.07 * image_scaled_height

# contains pair of (y,x) tuples representing the printable rectangle of the image
area_whitelist = [(0.015, 0.015), (0.985, 0.985)]

# contains pairs of (y,x) tuples representing the non-printable regions within the whitelist region
area_blacklist = list()

# toggle to store whether the user wants to find nodules
search_for_nodules = True

# toggle to store whether the user wants to test radii
test_radii = False

# number of radius test images to output
testcase_count = 50

dpi = 0

threshold_multiplier = 1

min_nodule_size = 12