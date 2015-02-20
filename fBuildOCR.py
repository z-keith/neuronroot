# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fBuildOCR
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    builds an over-complete representation of an input image
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import networkx as nx
import math

# Class import declarations
from cRoot import Node

# Function import declarations

def ConstructOCR(ImgArray):
#### Default seed point for the image
    seedxy = (1146, 80)
#### This needs to be replaced with a user input prompt (probably click-based)

    dist_seed_best = 999999     #current distance from the seed point
    node_best = None    #current candidate node
    
    graph = nx.Graph()
    xsize = ImgArray.shape[1]
    ysize = ImgArray.shape[0]
    nodecount = 0
    
    node_dict = {}  #keys = graph node name(int), values = Node objects
    
    for y in range (0, ysize):
#### Debugging percentage-complete calculator
        if (y%500 == 0):
            print('Finding nodes: ' + str(round((100*y/ysize), 1)) + '%')
#### Remove/rework as display in final version       
        
        for x in range (0, xsize):
            if(ImgArray[y][x] > 0): #only creates nodes out of pixels greater than the global threshold
                node_dict[nodecount] = Node(x, y, ImgArray[y][x]*255) #scale intensity to 255 (just easier to read and work with)
                graph.add_node(nodecount) #the value of nodecount is being used as the name/label for each node
                nodecount += 1
    nx.convert_node_labels_to_integers(graph, first_label=0)               
     
    nodesprinted = 0 #this is only used in the progress bar, otherwise safe for deletion
    totalnodes = graph.number_of_nodes()
    
    for node1 in graph: #find node that best approximates seed location
        dist_seed_this = math.sqrt((seedxy[0]-node_dict[node1].X)**2 + (seedxy[1]-node_dict[node1].Y)**2)
        if  dist_seed_this < dist_seed_best:
            dist_seed_best = dist_seed_this
            node_best = node1

#### Debugging percentage-complete calculator
        if (nodesprinted%10000 == 0):
            print('Creating edges: ' + str(round((100*nodesprinted/totalnodes), 1)) + '%')
        nodesprinted += 1
#### Remove/rework as display in final version       
        
        for node2 in range(MinFunc(node1, ysize), MaxFunc(node1, ysize, totalnodes)):
            # The range is currently set to (current node - x, current node + x) where x = pixels in one column
            # of the image. This is purposely conservative  to make sure it accounts for the possibility of every pixel
            # being a valid node (which will never happen in normal operation.) This could be much more efficiently
            # written (possibly as a switch statement iterating 1-8 to get each adjacent pixel)
            if abs(node_dict[node1].X - node_dict[node2].X) <= 1:
                if abs(node_dict[node1].Y - node_dict[node2].Y) <= 1:
                    if node1 != node2:
                        weightval = CalculateWeight(node_dict[node1].Intensity, node_dict[node2].Intensity, 225)
                        graph.add_edge(node1, node2)
                        graph[node1][node2]['weight'] = weightval
                        
    pred, distance = nx.dijkstra_predecessor_and_distance(graph, node_best) #note: distance is not used for anything

    for key in pred:
        if len(pred[key]) > 0:
            node_dict[key].Parent = int(pred[key][0])
            node_dict[int(pred[key][0])].Children.append(key)

    #at this point. node_dict should contain all nodes and their parents and children.
    #that's basically a tree! it also has easy access to x, y, i, and r
    #as long as I don't need edge weights (which can be recalculated), can safely return
    #node_dict and move on to pruning dark/redundant nodes

    print(graph.number_of_edges())
    print(graph.number_of_nodes())


    return node_dict                           
    
def CalculateWeight(intensity1, intensity2, intensitymax):
    #formula taken from Peng et al section 2.2
    result1 = math.exp(10*((1-intensity1)/intensitymax)**2)
    result2 = math.exp(10*((1-intensity2)/intensitymax)**2)
    return (result1+result2)/2
    
def MinFunc(node1, maxsize):
    if (node1 - 1.01*maxsize) > 0:
        return int(node1 - 1.01*maxsize)
    else:
        return 0
    
def MaxFunc(node1, maxsize, nodecount):
    if (node1 + 1.01*maxsize) < (nodecount - 1):
        return int(node1 + 1.01*maxsize)
    else:
        return (nodecount-1)