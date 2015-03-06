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

# Function import declarations


def ConstructOCR(ImgArray):
    graph = nx.Graph()
    nodecount = 0

    node_dict = {}  #keys = graph node name(int), values = Node objects
    
    for y in range (0, config.sizeY):
        for x in range (0, config.sizeX):
            #only creates nodes out of pixels greater than the global threshold
            if(ImgArray[y][x] > 0):
            #current value of nodecount is used for the key to node_dict and for
            #the node label in the graph, to keep the two associated
                node_dict[nodecount] = Node(x, y, ImgArray[y][x]/255)
                graph.add_node(nodecount)
                nodecount += 1
    nx.convert_node_labels_to_integers(graph, first_label=0) 
    
    print ("Created nodes in " + config.PrintTimeBenchmark())
    print ("Found " + str(graph.number_of_nodes()) + " nodes.")
    config.initial_nodecount = nodecount

    #set dummy for a node that approximates the config.seed point
    dist_seed_best = 999999     #current distance from the seed point
    node_best = 0    #current candidate node

    for node1 in graph:
        #check if this is the node that best approximates seed point location
        dist_seed_this = math.sqrt((config.seedX - node_dict[node1].X)**2 + (config.seedY - node_dict[node1].Y)**2)
        if  dist_seed_this < dist_seed_best:
            dist_seed_best = dist_seed_this
            node_best = node1
        
        #create the edges that extend ahead of the current node
        NodeCheckRight(node_dict, graph, node1)
        NodeCheckDownLeft(node_dict, graph, node1)
        NodeCheckDown(node_dict, graph, node1)
        NodeCheckDownRight(node_dict, graph, node1)
    
    print ("Added and weighted edges in " + config.PrintTimeBenchmark())
    print ("Found " + str(graph.number_of_edges()) + " edges.")
    
    #build initial tree from node_best
    treecount  = 0
    ConstructPartialTree(graph, node_dict, node_best)

    #find additional trees that were detached
    for key in node_dict:
        if key in graph:
            if len(graph[key]) == 8:
                if ConstructPartialTree(graph, node_dict, key):
                    treecount += 1
                
    print ("Detected additional trees in " + config.PrintTimeBenchmark())
    print("Found " + str(treecount) + " trees.")
        
    #We will probably need to add node_best to the return

    return node_dict 

def NodeCheckRight(node_dict, graph, node1):
    node2loc = (node_dict[node1].X + 1, node_dict[node1].Y)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)

def NodeCheckDownLeft(node_dict, graph, node1):
    node2loc = (node_dict[node1].X - 1, node_dict[node1].Y + 1)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)

def NodeCheckDown(node_dict, graph, node1):
    node2loc = (node_dict[node1].X, node_dict[node1].Y + 1)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)
                
def NodeCheckDownRight(node_dict, graph, node1):
    node2loc = (node_dict[node1].X + 1, node_dict[node1].Y + 1)
    NodeCheckingMechanism(node1, node2loc, node_dict, graph)
                
def NodeCheckingMechanism(node1, node2loc, node_dict, graph):
    for node2 in range(node1, MaxRange(node1, graph.number_of_nodes())):
        if (node_dict[node2].X == node2loc[0]):
            if (node_dict[node2].Y == node2loc[1]):
                edge_weight = CalculateWeight(node_dict[node1].Intensity, node_dict[node2].Intensity)
                graph.add_edge(node1, node2)
                graph[node1][node2]['weight'] = edge_weight
                break
                
def MaxRange(node1, nodecount):
    #calculates the index within node_dict of the last possible node that could represent the pixel one down and one to
    #the right from the current node1. If the entire image is made of nodes, this index is node1 + the width of the
    #image + 2, for a complete line across the image plus the pixel below and below-right (the target)
    if (node1 + config.sizeY + 2) < (nodecount - 1):
        return (node1 + config.sizeY + 2)
    else:
        return (nodecount -1)    
    
def CalculateWeight(intensity1, intensity2):
    #formula taken from Peng et al section 2.2
    result1 = math.exp(10*(1-intensity1)**2)
    result2 = math.exp(10*(1-intensity2)**2)
    return (result1+result2)/2

def ConstructPartialTree(graph, node_dict, seed_node):
    pred_dict, distance_dict = nx.dijkstra_predecessor_and_distance(graph, seed_node)
    sig_tree = TreeCheck(pred_dict, node_dict)
    # set parent/children relationships
    for key in pred_dict:
        if len(pred_dict[key]):
            if sig_tree:            
                node_dict[key].Parent = int(pred_dict[key][0])
                node_dict[int(pred_dict[key][0])].Children.append(key)
            graph.remove_node(key)
    return sig_tree
            
def TreeCheck(pred_dict, node_dict):
    minX = 99999
    maxX = 0
    minY = 99999
    maxY = 0
    count = 0
    for key in pred_dict:        
        if len(pred_dict[key]):
            count += 1
            if node_dict[key].X < minX:
                minX = node_dict[key].X
            if node_dict[key].X > maxX:
                maxX = node_dict[key].X
            if node_dict[key].Y < minY:
                minY = node_dict[key].Y
            if node_dict[key].Y > maxY:
                maxY = node_dict[key].Y
    if maxY > 0.999*config.sizeY:
        return False
    else:
        return (count>0.75*config.sizeY)