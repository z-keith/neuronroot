# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       area_builder.py
#   author=     Zackery Keith
#   date=       Jul 2 2015
#   purpose=    Converts an array of intensities into a pixel_dict full of Pixels and their neighbor relationships,
#               representing continuous areas of the image
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
import pixel as px


class AreaBuilder:

    # Dictionary of the form {(int y, int x) : Pixel} that will hold the reconstruction areas
    # WARNING: TreeBuilder makes a shallow copy of this pixel_dict, and changes to one affect the other. After the
    # controller initializes TreeBuilder, this dictionary becomes unreliable.
    pixel_dict = None

    def __init__(self):
        self.pixel_dict = dict()

    def load_pixels(self, image_array):
        """
        Creates a pixel_dict from the output of an ArrayBuilder.
        :param image_array: a 2D numpy array of values between 0 and 255 inclusive. Represents the black and white
        filtered image created by an ArrayBuilder.
        :return: Nothing.
        """
        for y in range(0, image_array.shape[0]):
            for x in range(0, image_array.shape[1]):
                if image_array[y][x]:
                    self.pixel_dict[(y, x)] = px.Pixel(x, y, image_array[y][x])

    def find_neighbors(self):
        """
        Calls search_in_direction for each pixel in the dictionary, to build the web of neighbor relationships
        :return: Nothing.
        """
        for key in self.pixel_dict:
            # If each pixel checks the same half of eight possible directions, they will tessellate to cover all
            # possible edges. By convention, we choose to choose the 4 pixels that extend towards the southeast corner
            # (that is, the locations immediately to the east, southeast, south, and southwest)
            for delta in [(0, 1), (1, -1), (1, 0), (1, 1)]:
                self.search_in_direction(key, delta)

    def search_in_direction(self, pixel1_key, delta):
        """
        Checks to see if a given pixel has a neighbor in a given direction, and if so, sets them as neighbors.
        :param pixel1_key: The (y,x) dictionary key of the start pixel
        :param delta: The (y,x) change in location we're looking for a neighbor in (all values should be -1, 0, or 1)
        :return: Nothing.
        """
        # Build the dictionary key that a potential neighbor would have
        pixel2_y = pixel1_key[0] + delta[0]
        pixel2_x = pixel1_key[1] + delta[1]
        pixel2_key = (pixel2_y, pixel2_x)

        # Check to see if the prospective key actually exists
        if pixel2_key in self.pixel_dict:
            self.pixel_dict[pixel1_key].set_neighbors(self.pixel_dict[pixel2_key])

    def set_radii(self):
        """
        Iterates through the pixels of a root structure setting the radius of each pixel. It can be assumed that any
        pixel that does not have 8 neighbors is touching black space and the maximum radius of a circle centered at the
        pixel and contained within the root is 0. It follows that all pixels touching that pixel (the second layer
        inward) have radius 1, and so on and so forth.
        :return: Nothing
        """
        # Find the initial set of pixels that touch black space
        outermost_pixel_set = set()
        for pixel in self.pixel_dict.values():
            if None in pixel.neighbors:
                outermost_pixel_set.add(pixel)

        # Iteratively assign radii to sets of nodes, making new sets out of the union of the current set's neighbors
        current_radius_value = 0
        while outermost_pixel_set:
            new_outermost_set = set()

            for pixel in outermost_pixel_set:
                pixel.radius = current_radius_value

            for pixel in outermost_pixel_set:
                for neighbor in pixel.neighbors:
                    if neighbor and neighbor.radius is None:
                        new_outermost_set.add(neighbor)

            current_radius_value += 1
            outermost_pixel_set = new_outermost_set
