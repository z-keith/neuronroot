# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fBuildOCR
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    builds an over-complete representation of an input image (with rewritten edge detection)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import networkx as nx
import math
import config

# Class import declarations
from cRoot import Node

def ConstructOCR(img_array):
    """
    Main construction function. Converts a numpy array to a dictionary containing interconnected Node objects
    :param img_array: numpy array of values 0-255 representing brightness at that location
    :return: node_dict of the form {int: Node} representing all trees constructed
    """
    # initialize containers and counter
    graph = nx.Graph()
    nodecount = 0
    node_dict = {}  # keys = graph node name(int), values = Node objects

    # create nodes out of locations of nonzero brightness
    for y in range (0, config.sizeY):
        for x in range (0, config.sizeX):
            if(img_array[y][x] > 0):
                # current value of nodecount is used for the key to node_dict and for the node label in the graph,
                # to keep the two associated. Intensity is mapped from 0-255 to 0-1 for readability.
                node_dict[nodecount] = Node(x, y, img_array[y][x]/255)
                graph.add_node(nodecount)
                nodecount += 1
    #may not need or want this:
    #nx.convert_node_labels_to_integers(graph, first_label=0)
    
    print ("Created nodes in {0}".format(config.PrintTimeBenchmark()))
    print ("Found {0} nodes.".format(graph.number_of_nodes()))
    config.initial_nodecount = nodecount

    # set dummy for a node that approximates the config.seed point
    dist_seed_best = 999999     #current distance from the seed point
    node_best = 0    #current candidate node

    for node1 in graph:
        # check if this is the node that best approximates seed point location
        dist_seed_this = math.sqrt((config.seedX - node_dict[node1].X)**2 + (config.seedY - node_dict[node1].Y)**2)
        if  dist_seed_this < dist_seed_best:
            dist_seed_best = dist_seed_this
            node_best = node1
        
        # create the edges that extend ahead of the current node
        NodeCheckRight(node_dict, graph, node1)
        NodeCheckDownLeft(node_dict, graph, node1)
        NodeCheckDown(node_dict, graph, node1)
        NodeCheckDownRight(node_dict, graph, node1)

    config.best_node = node_best
    
    print ("Added and weighted edges in {0}".format(config.PrintTimeBenchmark()))
    print ("Found {0} edges.".format(graph.number_of_edges()))
    
    # build initial tree from node_best
    treecount  = 0
    ConstructPartialTree(graph, node_dict, node_best)

    # find additional trees that were detached
    for key in node_dict:
        if key in graph:
            # look only for nodes that are completely surrounded by other nodes
            if len(graph[key]) == 8:
                if ConstructPartialTree(graph, node_dict, key):
                    treecount += 1
                
    print ("Detected additional trees in {0}".format(config.PrintTimeBenchmark()))
    print("Found {0} trees.".format(treecount))
        
    # We will probably need to add node_best to the return
    return node_dict 


def NodeCheckRight(node_dict, graph, node1):
    """
    Sets up NodeCheckingMechanism to check the pixel to the right of a node.
    :param node_dict: dict of the form {int: Node} to search
    :param graph: graph to pass to NodeCheckingMechanism
    :param node1: node to search from
    """
    node2loc = (node_dict[node1].X + 1, node_dict[node1].Y)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)


def NodeCheckDownLeft(node_dict, graph, node1):
    """
    Sets up NodeCheckingMechanism to check the pixel to the bottom-left of a node.
    :param node_dict: dict of the form {int: Node} to search
    :param graph: graph to pass to NodeCheckingMechanism
    :param node1: node to search from
    """
    node2loc = (node_dict[node1].X - 1, node_dict[node1].Y + 1)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)


def NodeCheckDown(node_dict, graph, node1):
    """
    Sets up NodeCheckingMechanism to check the pixel below a node.
    :param node_dict: dict of the form {int: Node} to search
    :param graph: graph to pass to NodeCheckingMechanism
    :param node1: node to search from
    """
    node2loc = (node_dict[node1].X, node_dict[node1].Y + 1)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)


def NodeCheckDownRight(node_dict, graph, node1):
    """
    Sets up NodeCheckingMechanism to check the pixel to the bottom-right of a node.
    :param node_dict: dict of the form {int: Node} to pass to NodeCheckingMechanism
    :param graph: graph to pass to NodeCheckingMechanism
    :param node1: the node to search from
    """
    node2loc = (node_dict[node1].X + 1, node_dict[node1].Y + 1)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)


def NodeCheckingMechanism(node1, node2loc, node_dict, graph):
    """
    Looks for a node in a specified location, and adds a weighted edge to it
    :param node1: the node to search from
    :param node2loc: a tuple containing the location to search for node2 in
    :param node_dict: dict of the form {int: Node} to search
    :param graph: graph to add the edge to
    """
    for node2 in range(node1, MaxRange(node1, graph.number_of_nodes())):
        if (node_dict[node2].X == node2loc[0]):
            if (node_dict[node2].Y == node2loc[1]):
                edge_weight = CalculateWeight(node_dict[node1].Intensity, node_dict[node2].Intensity)
                graph.add_edge(node1, node2)
                graph[node1][node2]['weight'] = edge_weight
                node_dict[node1].Neighbors.add(node2)
                node_dict[node2].Neighbors.add(node1)
                break


def MaxRange(node1, nodecount):
    """
    calculates the index within node_dict of the last possible node that could represent the pixel one down and one to
    the right from the current node1. If the entire image is made of nodes, this index is node1 + the height of the
    image + 2, for a complete line across the image plus the pixel to the right and below-right (the target)
    :param node1: node to search from
    :param nodecount: the total number of nodes (so the function doesn't return an invalid index)
    :return: the maximum location of an adjacent node
    """
    if (node1 + config.sizeY + 2) < (nodecount - 1):
        return (node1 + config.sizeY + 2)
    else:
        return (nodecount -1)

    
def CalculateWeight(intensity1, intensity2):
    """
    formula taken from Peng et al section 2.2 to calculate the weight of an edge between 2 nodes
    :param intensity1: intensity of node 1
    :param intensity2: intensity of node 2
    :return: float indicating the proper weight
    """
    result1 = math.exp(10*(1-intensity1)**2)
    result2 = math.exp(10*(1-intensity2)**2)
    return (result1+result2)/2


def ConstructPartialTree(graph, node_dict, seed_node):
    """

    :param graph: graph to search
    :param node_dict: dict of the form {int: Node} to search
    :param seed_node: key of node to start from
    :return: boolean representing if seed_node was part of a valid tree
    """
    # construct paths to all connectable nodes
    pred_dict, distance_dict = nx.dijkstra_predecessor_and_distance(graph, seed_node)

    # check if tree is significantly large (and not a ruler)
    sig_tree = TreeCheck(pred_dict, node_dict)

    # set parent/children relationships between nodes if the tree is significant
    for key in pred_dict:
        if len(pred_dict[key]):
            if sig_tree:            
                node_dict[key].Parent = int(pred_dict[key][0])
                node_dict[int(pred_dict[key][0])].Children.add(key)
            graph.remove_node(key)

    return sig_tree


def TreeCheck(pred_dict, node_dict):
    """
    checks if a potential tree has enough nodes to be significant, and if the tree touches the bottom of the image
    if it does, it's the ruler
    :param pred_dict: dictionary of the path back to a seed point from each node
    :param node_dict: dict of the form {int: Node} to get location info from
    :return: boolean representing if pred_dict represents a valid tree
    """
    maxY = 0
    count = 0

    #count the nodes and track their Y locations
    for key in pred_dict:        
        if len(pred_dict[key]):
            count += 1
            if node_dict[key].Y > maxY:
                maxY = node_dict[key].Y

    # does the tree get within (based on 2000px height) 1 px of the edge?
    if maxY > 0.999*config.sizeY:
        return False
    # is the tree at least (based on 2000px height) 1500 px in area?
    else:
        return (count>0.75*config.sizeY)