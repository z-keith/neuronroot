# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       array_builder.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Loads the input image and prepares it for analysis
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from PIL import Image
from scipy import ndimage
import numpy as np
import warnings

# noinspection PyUnresolvedReferences
import config


class ArrayBuilder:

    # File name stub to be loaded (in production version, will have to change to file path)
    file_name = None

    # Stores the thresholded, filtered, and masked image data for delivery to another function
    array = None

    # Stores the image for use in the UI
    UI_image = None

    # Image dimensions
    image_height = None
    image_width = None

    def __init__(self, filename):
        self.file_name = filename

    def load_to_array(self):
        """
        Loads and scales the image from the file name defined when this ArrayBuilder was initialized.
        :return: Nothing.
        """
        warnings.simplefilter('ignore', Image.DecompressionBombWarning)
        image = Image.open("../TestImages/{0}.tif".format(self.file_name))

        if image.info['dpi'][0]:
            config.cm_per_pixel = 1 / (image.info['dpi'][0] / 2.54)
            config.dpi = image.info['dpi'][0]

        # Scale the image down, if necessary, to the height defined in config
        # The program can be made to run faster at the cost of precision by reducing config.image_scaled_height
        scaling_ratio = (config.image_scaled_height / float(image.size[1]))
        if scaling_ratio < 1:
            scaled_width = int(float(image.size[0])*scaling_ratio)
            image = image.resize((scaled_width, config.image_scaled_height))
            config.cm_per_pixel /= scaling_ratio

        self.image_height = image.size[1]
        self.image_width = image.size[0]

        self.array = np.array(image)

    def filter_array(self):
        """
        Changes the array to represent a black and white image and thresholds it at a percentage of the global mean
        :return: Nothing.
        """
        self.array = np.dot(self.array[..., :3], [0.299, 0.587, 0.144])

        # Scale of the image mean intensity to threshold the image at (higher multipliers are less permissive)
        threshold_multiplier = 1.0

        global_threshold = self.array.mean() * threshold_multiplier
        self.array[self.array < global_threshold] = 0

        self.array = ndimage.filters.median_filter(self.array, size=(4, 4))

    def mask_ruler(self):
        """
        Automatically sets the margins of the image and the region containing the ruler to black, to prevent image
        artifacts from being detected as roots.
        :return: Nothing.
        """

        # Find the locations of the edges of the whitelisted area
        left_margin = int(config.area_whitelist[0][1]*self.image_width)
        right_margin = int(config.area_whitelist[1][1]*self.image_width)
        top_margin = int(config.area_whitelist[0][0]*self.image_height)
        bottom_margin = int(config.area_whitelist[1][1]*self.image_height)

        # Left edge
        for x in range(0, left_margin):
            for y in range(0, self.image_height):
                self.array[y, x] = 0

        # Right edge
        for x in range(right_margin, self.image_width):
            for y in range(0, self.image_height):
                self.array[y, x] = 0

        # Top edge
        for x in range(left_margin, right_margin):
            for y in range(0, top_margin):
                self.array[y, x] = 0

        # Bottom edge
        for x in range(left_margin, right_margin):
            for y in range(bottom_margin, self.image_height):
                self.array[y, x] = 0

        # Blacklisted areas
        for area in config.area_blacklist:
            yrange = (int(area[0][0]*self.image_height), int(area[1][0]*self.image_height))
            xrange = (int(area[0][1]*self.image_width), int(area[1][1]*self.image_width))
            for y in range(yrange[0], yrange[1]):
                for x in range(xrange[0], xrange[1]):
                    self.array[y, x] = 0

        self.UI_image = Image.fromarray(self.array, 'RGB')
