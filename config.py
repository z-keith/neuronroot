class Config:
    # default input/output locations, (defaults are relative paths, but absolute paths are permissible)
    infile_path = "TestImages/"
    outfile_path = "Output/"

    # file extension to generate output with
    # by default, QT does not support .tiff files, so they are converted to this type for display
    proper_file_extension = ".jpg"

    # default height to scale images to (0 means never scale)
    image_scaled_height = 2000

    # default minimum area of a tree
    # stored as a percentage of the image's height
    minimum_tree_size_multiplier = 0.07

    # default thresholding value to separate root from background
    # increasing the threshold can help to clean up images with relatively bright backgrounds
    threshold_multiplier = 1

    # default minimum radius of a nodule
    # increasing this value will remove false positives in nodule detection, at the cost of missing smaller nodules
    # note: deprecated in 1.2.0
    # min_nodule_size = 0

    # nodule detection thresholds:
    # any location larger than this*image average radius is automatically a nodule
    # higher values result in less reliable detection for nodules that are very large
    abs_threshold_multiplier = 5
    # no location smaller than this*image average radius is eligible to be a nodule
    # higher values result in less detection of small nodules
    min_threshold_multiplier = 2
    # used for adaptive nodule detection
    # higher values result in nodules only being found at rapidly-growing points
    # lower values result in more nodule detections but possibly more errors
    rad_multiplier = 1.5

    # contains pair of (y,x) tuples representing the part of the image worth analyzing
    # y and x are stored as percentages of the image dimensions
    # by default, ignores the outermost 1.5% of the image
    area_whitelist = [(0.015, 0.015), (0.985, 0.985)]

    # contains pairs of (y,x) tuples representing the non-printable regions within the whitelist region
    # y and x are stored as percentages of the image dimensions
    # by default, the blacklist is empty
    area_blacklist = []

    # default DPI value
    # used to calculate real-life sizes from pixel sizes
    # if the roots were scanned, the dpi stored in the image file will be accurate
    # photographs of roots will require manual DPI calculation
    dpi = 1200

    # if true, the program will run the nodule-searching subroutine
    # set this to false if you don't care about nodules
    search_for_nodules = True

    # DEVELOPER OPTIONS
    # toggle to store whether the user wants to test radii calculation with test-printed images
    # you more than likely don't want this option
    test_radii = False
    # number of radius test images to output
    # only used when test_radii is true
    testcase_count = 50

    # PROGRAM VARIABLES
    # do not edit these values - they're just enumerated here to track what's being stored in this class
    file_name = None
    file_extension = None

    initial_image_path = None
    updated_image_path = None

    image_dimensions = None
    cm_per_pixel = None
    seedYX = None
