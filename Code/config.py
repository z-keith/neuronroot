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
minimum_tree_size = 0.10 * image_scaled_height

# contains pair of (y,x) tuples representing the printable rectangle of the image
area_whitelist = None

# contains pairs of (y,x) tuples representing the non-printable regions within the whitelist region
area_blacklist = []

# toggle to store whether the user wants to find nodules
search_for_nodules = True

# toggle to store whether the user wants to test radii
test_radii = False

# number of radius test images to output
testcase_count = 50

dpi = 0


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

    if current_file == 308:
        multiplier = image_scaled_height/9840
        file_name = "2014-08-7-Tri308"
        seedYX = (int(784*multiplier), int(6672*multiplier))
        cm_per_pixel = 1/(470*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 311:
        multiplier = image_scaled_height/17089
        file_name = "2014-08-7-Tri311"
        seedYX = (int(12075*multiplier), int(6695*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 315:
        multiplier = image_scaled_height/20256
        file_name = "2014-08-7-Tri315"
        seedYX = (int(4608*multiplier), int(2656*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 317:
        multiplier = image_scaled_height/20256
        file_name = "2014-08-7-Tri317"
        seedYX = (int(8928*multiplier), int(12060*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 320:
        multiplier = image_scaled_height/3515
        file_name = "2014-08-7-Tri320"
        seedYX = (int(335*multiplier), int(1540*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.65, 0), (1, 1))]

    if current_file == 324:
        multiplier = image_scaled_height/9825
        file_name = "2014-08-7-Tri324"
        seedYX = (int(7200*multiplier), int(208*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.85, 0), (1, 0.4))]

    if current_file == 326:
        multiplier = image_scaled_height/9750
        file_name = "2014-08-8-Tri326"
        seedYX = (int(5104*multiplier), int(7040*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 328:
        multiplier = image_scaled_height/9305
        file_name = "2014-08-8-Tri328"
        seedYX = (int(4928*multiplier), int(7312*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 329:
        multiplier = image_scaled_height/8032
        file_name = "2014-06-26-Tri-329"
        seedYX = (int(1729*multiplier), int(3613*multiplier))
        cm_per_pixel = 1/(470*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 335:
        multiplier = image_scaled_height/20157
        file_name = "2014-08-8-Tri335"
        seedYX = (int(768*multiplier), int(13504*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.65, 0), (1, 0.3))]

    if current_file == 426:
        multiplier = image_scaled_height/7172
        file_name = "2014-08-14-Tri-426"
        seedYX = (int(1393*multiplier), int(6674*multiplier))
        cm_per_pixel = 1/(470*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 427:
        multiplier = image_scaled_height/14344
        file_name = "2014-08-14-Tri-427"
        seedYX = (int(4578*multiplier), int(13346*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 428:
        multiplier = image_scaled_height/9914
        file_name = "2014-08-14-Tri-428"
        seedYX = (int(5697*multiplier), int(6513*multiplier))
        cm_per_pixel = 1/(470*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 429:
        multiplier = image_scaled_height/19829
        file_name = "2014-08-14-Tri-429"
        seedYX = (int(11136*multiplier), int(12864*multiplier))
        cm_per_pixel = 1/(470*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 446:
        multiplier = image_scaled_height/9985
        file_name = "2014-08-18-Tri446"
        seedYX = (int(5152*multiplier), int(6096*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 449:
        multiplier = image_scaled_height/19970
        file_name = "2014-08-18-Tri449"
        seedYX = (int(15456*multiplier), int(9344*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 455:
        multiplier = image_scaled_height/18938
        file_name = "2014-08-18-Tri455"
        seedYX = (int(800*multiplier), int(11936*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0), (1, 0.6))]

    if current_file == 459:
        multiplier = image_scaled_height/19173
        file_name = "2014-08-18-Tri459"
        seedYX = (int(12800*multiplier), int(6784*multiplier))
        cm_per_pixel = 1/(940*multiplier)
        area_whitelist = [(0.015, 0.015), (0.985, 0.985)]
        area_blacklist = [((0.8, 0.6), (1, 1))]

