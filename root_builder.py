# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       root_builder.py
#   author=     Zackery Keith
#   date=       Jul 6 2015
#   purpose=    Builds roots from a pixel_dict skeleton, removes invalid roots, and disentangles them to create an
#               accurate representation of the source root
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class RootBuilder:
    # Contains the tree structures being built in the format {(int y, int x) : Pixel}
    # WARNING: This is only a shallow copy of TreeBuilder's pixel_dict, and changes to one affect the other.
    pixel_dict = None

    def __init__(self, pixel_dict):
        self.pixel_dict = pixel_dict
