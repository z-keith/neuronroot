# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       main.py
#   author=     Zackery Keith
#   date=       May 29 2015
#   purpose=    Calls and manipulates the controller to perform an iteration of the analysis algorithm
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# noinspection PyUnresolvedReferences
import controller
# noinspection PyUnresolvedReferences
import config


def compare_two_iterations():
    c1 = controller.Controller()

    c1.load_image_to_array()
    c1.build_areas()
    c1.build_trees()

    c2 = controller.Controller()

    c2.load_image_to_array()
    c2.build_areas()
    c2.build_trees()

    set1 = set()
    set2 = set()

    for key in c1.tree_builder.pixel_dict.keys():
        set1.add(key)
    for key in c2.tree_builder.pixel_dict.keys():
        set2.add(key)

    print("\nPixels")
    print("Length of c1: " + str(len(set1)))
    print("Length of c2: " + str(len(set2)))

    c1.build_roots()
    c2.build_roots()

    set1 = set()
    set2 = set()
    for key in c1.root_builder.pixel_dict.keys():
        set1.add(key)
    for key in c2.root_builder.pixel_dict.keys():
        set2.add(key)

    set3 = set()
    set4 = set()
    for key in c1.root_builder.root_dict.keys():
        set3.add(key)
    for key in c2.root_builder.root_dict.keys():
        set4.add(key)

    print("\nPost-root-build Pixels")
    print("Length of c1: " + str(len(set1)))
    print("Length of c2: " + str(len(set2)))

    print("\nRoots")
    print("Length of c1: " + str(len(set3)))
    print("Length of c2: " + str(len(set4)))

def main():
    """
    Function called on program initialization
    """

    # initialize the Controller object
    current_controller = controller.Controller()

    # load the image file into an ArrayBuilder
    current_controller.load_image_to_array()

    # construct a graph and associated node_dict in a AreaBuilder
    current_controller.build_areas()

    # print the initial representation of the output with a new Printer
    current_controller.print_background()

    # prune the initial representation down to a skeleton with a TreeBuilder
    current_controller.build_trees()

    # reuse the Printer to print the skeleton representation of the output
    current_controller.print_skeleton()

    # build root structures with a RootBuilder
    current_controller.build_roots()

    # reuse the Printer to print a representation of the roots
    current_controller.print_roots()

    # complete!
    print("\n#####################################################################")
    print("#\t Program complete! Total runtime: {0}\t#".format(current_controller.print_total_time()))
    print("#####################################################################")

for val in [293, 329, 426, 427, 428]:
    config.current_file = val
    main()

# compare_two_iterations()
