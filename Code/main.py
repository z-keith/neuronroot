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

    if config.test_radii:
        # reuse the Printer to print radius test images
        current_controller.print_test_radii()

    # prune the initial representation down to a skeleton with a TreeBuilder
    current_controller.build_trees()

    # reuse the Printer to print the skeleton representation of the output
    current_controller.print_skeleton()

    # build root structures with a RootBuilder
    current_controller.build_roots()

    # reuse the Printer to print a representation of the roots
    current_controller.print_roots()

    # if the user selected it, search for nodules
    if config.search_for_nodules:
        current_controller.find_nodules()

        # and print them
        current_controller.print_nodules()

    # complete!
    print("\n#####################################################################")
    print("#\t Program complete! Total runtime: {0}\t#".format(current_controller.print_total_time()))
    print("#####################################################################")

for val in [293, 329, 426, 427, 428]: # 293, 329, 426, 427, 428]:
    config.current_file = val
    main()
