from PIL import Image
from scipy import ndimage
import numpy as np


class ArrayBuilder:
    # File name stub to be loaded (in production version, will have to change to file path)
    file_path = None

    # Stores the thresholded, filtered, and masked image data for delivery to another function
    array = None

    # Stores the image for use in the UI
    UI_image = None

    # Image dimensions
    image_height = None
    image_width = None

    def __init__(self, file_path):
        self.file_path = file_path

    def load_to_array(self, max_height):
        image = Image.open(self.file_path)

        # if 'dpi' in image.info:
        #     if image.info['dpi'][0]:
        #         cm_per_pixel = 1 / (image.info['dpi'][0] / 2.54)
        #         dpi = image.info['dpi'][0]

        # Scale the image down, if necessary, to the height defined in config
        # The program can be made to run faster at the cost of precision by reducing config.image_scaled_height
        scaling_ratio = 1
        if max_height:
            scaling_ratio = (max_height / float(image.size[1]))
            if scaling_ratio < 1:
                scaled_width = int(float(image.size[0]) * scaling_ratio)
                image = image.resize((scaled_width, max_height))

        self.image_height = image.size[1]
        self.image_width = image.size[0]

        self.array = np.array(image)

        if max_height and scaling_ratio < 1:
            return (self.image_height, self.image_width), scaling_ratio
        else:
            return (self.image_height, self.image_width), 1

    def filter_array(self, threshold_multiplier):
        self.array = np.dot(self.array[..., :3], [0.299, 0.587, 0.144])

        # Scale of the image mean intensity to threshold the image at (higher multipliers are less permissive)
        global_threshold = self.array.mean() * threshold_multiplier
        self.array[self.array < global_threshold] = 0

        self.array = ndimage.filters.median_filter(self.array, size=(4, 4))

    def mask_ruler(self, whitelist, blacklist):

        # Find the locations of the edges of the whitelisted area
        left_margin = int(whitelist[0][1] * self.image_width)
        right_margin = int(whitelist[1][1] * self.image_width)
        top_margin = int(whitelist[0][0] * self.image_height)
        bottom_margin = int(whitelist[1][1] * self.image_height)

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
        for area in blacklist:
            yrange = (abs(int(area[0][0] * self.image_height)), abs(int(area[1][0] * self.image_height)))
            xrange = (abs(int(area[0][1] * self.image_width)), abs(int(area[1][1] * self.image_width)))
            for y in range(yrange[0], yrange[1]):
                for x in range(xrange[0], xrange[1]):
                    if x < self.array.shape[1] and y < self.array.shape[0]:
                        self.array[y, x] = 0

        self.UI_image = Image.fromarray(self.array, 'RGB')
