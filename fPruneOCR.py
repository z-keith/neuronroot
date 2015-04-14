 #-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fPruneOCR
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    Removes redundant nodes from an OCR
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import config


def PruneOCR(node_dict):
    """
    Main pruning function, prints debug data and calls RemoveDark and RemoveRedundant
    :param node_dict: dictionary of form {int: Node}
    :return: node_dict, but stripped of dark/redundant nodes
    """
    node_dict = RemoveDark(node_dict)

    remaining_nodecount = len(node_dict)
    removed_count = config.initial_nodecount - remaining_nodecount
    print("Removed dark leaves in {0}".format(config.PrintTimeBenchmark()))
    print("Removed {0} dark nodes.".format(removed_count))

    node_dict = SetRadii(node_dict)
    print("Set radii in {0}".format(config.PrintTimeBenchmark()))

    node_dict = RemoveRedundant(node_dict)

    post_rmdark_nodecount = remaining_nodecount
    remaining_nodecount = len(node_dict)
    removed_count = post_rmdark_nodecount - remaining_nodecount
    print("Removed redundant nodes in {0}".format(config.PrintTimeBenchmark()))
    print("Removed {0} redundant nodes.".format(removed_count))

    print("Total nodes in final representation: {0}".format(str(remaining_nodecount)))
    compression_percentage = round(100 * (1 - remaining_nodecount / config.initial_nodecount), 1)
    print("Compression: {0}%".format(compression_percentage))

    return node_dict


def RemoveDark(node_dict):
    """
    Recursively removes leaf nodes that are not visibly bright, but were allowed into
    the image for construction purposes. Does so until all leaf nodes are visible.
    :param node_dict: dictionary of form {int: Node}
    :return: node_dict, but stripped of dark nodes
    """
    MINIMUM_VISIBLE_INTENSITY = 0.12

    while True:
        leafset = []
        removeset = []

        for key in node_dict:
            if not node_dict[key].Children:
                if not node_dict[key].Parent:
                    # remove any nodes with no children or parents (i.e: noise)
                    removeset.append(key)
                else:
                    # add nodes with no children to the set of leaf nodes
                    leafset.append(key)

        # remove noise
        for key in removeset:
            RemoveNode(node_dict, key)

        # check if the entire leafset is visible yet
        leafset_was_visible = True
        for key in leafset:
            if node_dict[key].Intensity < MINIMUM_VISIBLE_INTENSITY:
                # node was not visible, remove it
                RemoveNode(node_dict, key)
                # not all nodes were visible
                leafset_was_visible = False

        #if the entire leafset was visible, you're done
        if leafset_was_visible:
            return node_dict


def RemoveRedundant(node_dict):
    """
    Implements the covered-leaf removal algorithm as described in Peng et al 2.3.2
    :param node_dict: dictionary of form {int: Node}
    :return: node_dict, but stripped of redundant nodes
    """

    COVERING_THRESHOLD=0.9

    while True:
        leaf_set = set()
        remove_set = set()
        for key in node_dict:
            if not node_dict[key].Children:
                leaf_set.add(key)
        for key in leaf_set:
            mass_node = MassOperator(node_dict, node_dict[key].Covers)
            covering_set = set()
            for covering_key in node_dict[key].CoveredBy:
                for i in node_dict[covering_key].Covers:
                    covering_set.add(i)
            covering_mass = MassOperator(node_dict, covering_set.intersection(node_dict[key].Covers))
            if covering_mass/mass_node >= COVERING_THRESHOLD:
                remove_set.add(key)
        if remove_set:
            for key in remove_set:
                RemoveNode(node_dict, key)
        else:
            return node_dict


def RemoveNode(node_dict, key):
    """
    Removes a node from the dictionary, connecting its parent and child nodes
    :param node_dict: dictionary of form {int: Node}
    :param key: integer key representing a Node in node_dict
    """
    if key in node_dict:
        # attach this node's children to this node's parent
        if node_dict[key].Children:
            for child_key in node_dict[key].Children:
                node_dict[child_key].Parent = node_dict[key].Parent
                # attach the parent to the child
                node_dict[key].Parent.Children.append(child_key)

        # remove this node's parent's reference to this node
        if node_dict[key].Parent:
            node_dict[node_dict[key].Parent].Children.remove(key)

        # remove Neighbor references
        if node_dict[key].Neighbors:
            for neighbor_key in node_dict[key].Neighbors:
                node_dict[neighbor_key].Neighbors.remove(key)

        # remove Cover/CoveredBy references
        if node_dict[key].Covers:
            for cover_key in node_dict[key].Covers:
                node_dict[cover_key].CoveredBy.discard(key)
        if node_dict[key].CoveredBy:
            for covered_key in node_dict[key].CoveredBy:
                node_dict[covered_key].Covers.discard(key)

        del node_dict[key]


def SetRadii(node_dict):
    """
    Iterates through the nodes of a root structure setting the radius of each node. It can be assumed that any node that
    does not have 8 neighbors is touching black space and the maximum radius of a circle centered at the node and
    contained within the root is 0. It follows that all nodes touching that node (the second layer inward) have radius 1,
    and so on and so forth.
    :param node_dict: dictionary of form {int: Node}
    :return: node_dict, with the nodes' radii filled in
    """

    # create set of nodes that touch the black
    outermost_node_set = set()
    for key in node_dict:
        neighbor_count = len(node_dict[key].Neighbors)
        if neighbor_count < 8:
            outermost_node_set.add(key)

    # recursively iterate through until all radii are set
    current_radius_value = 0
    while outermost_node_set:
        new_outermost_set = set()

        # set current list's radii first, to avoid conflicts
        for key in outermost_node_set:
            node_dict[key].Radius = current_radius_value

        # add all nodes that a) touch the current set and b) haven't had a radius set yet
        for key in outermost_node_set:
            for neighbor_key in node_dict[key].Neighbors:
                if node_dict[neighbor_key].Radius == -1:
                    new_outermost_set.add(neighbor_key)

        # increment current radius, reloop
        current_radius_value += 1
        outermost_node_set = new_outermost_set

    node_dict = SetCoveredSquares(node_dict)
    #node_dict = RefineCoveredRegions(node_dict)

    print("Max radius: {0}".format(current_radius_value))

    return node_dict

def SetCoveredSquares(node_dict):
    """
    Sets the Covers and CoveredBy fields to a square centered at each node in a node_dict
    :param node_dict: node_dict to operate on
    :return: node_dict with fields set
    """
    # set the nodes that are covered by each node
    for key in node_dict:
        node_dict[key].Covers.add(key)

        old_cover_set = set()
        old_cover_set.add(key)

        for i in range(node_dict[key].Radius):
            cover_set = set()
            for cover_node_key in old_cover_set:
                for neighbor_key in node_dict[cover_node_key].Neighbors:
                    cover_set.add(neighbor_key)
            for node_key in cover_set:
                node_dict[key].Covers.add(node_key)
                node_dict[node_key].CoveredBy.add(key)

    return node_dict

def RefineCoveredRegions(node_dict):
    """

    :param node_dict:
    :return:
    """
    for key in node_dict:
        X = node_dict[key].X
        Y = node_dict[key].Y
        Radius = node_dict[key].Radius
        remove_set = set()
        for covers_key in node_dict[key].Covers:
            X2 = node_dict[covers_key].X
            Y2 = node_dict[covers_key].Y
            if (X - X2)**2 + (Y - Y2)**2 > Radius**2:
                remove_set.add(covers_key)
        for remove_key in remove_set:
            node_dict[key].Covers.remove(remove_key)
            node_dict[remove_key].CoveredBy.remove(key)
    return node_dict

def MassOperator(node_dict, node_set):
    """
    Mass-computing operator for a set of nodes. Sums their intensity and returns it.
    :param node_dict: dictionary of form {int: Node}
    :param node_set: Set of unique keys that represent node_dict entries
    :return: Float representing the mass of the set of nodes
    """

    sum = 0.0
    for key in node_set:
        sum += node_dict[key].Intensity

    return sum