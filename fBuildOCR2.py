# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fBuildOCR2
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    builds an over-complete representation of an input image (with rewritten edge detection)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import networkx as nx
import math
import time

# Class import declarations
from cRoot import Node

# Function import declarations

def ConstructOCR(ImgArray):  
    lasttime = time.time()
    graph = nx.Graph()
    xsize = ImgArray.shape[1]
    ysize = ImgArray.shape[0]
    nodecount = 0
    
    node_dict = {}  #keys = graph node name(int), values = Node objects
    
    for y in range (0, ysize):         
        for x in range (0, xsize):
            #only creates nodes out of pixels greater than the global threshold
            if(ImgArray[y][x] > 0):
            #current value of nodecount is used for the key to node_dict and for
            #the node label in the graph, to keep the two associated
                node_dict[nodecount] = Node(x, y, ImgArray[y][x]/255)
                graph.add_node(nodecount)
                nodecount += 1
    nx.convert_node_labels_to_integers(graph, first_label=0) 
    
    print ("Constructed graph in " + PrintTimeBenchmark(lasttime))
    lasttime = time.time()
    print ("Nodes in initial representation: " + str(graph.number_of_nodes()))

    #### Default seed point for the image
    #seedxy = (1146, 80) #for 293
    seedxy = (901, 432) #for 329
    dist_seed_best = 999999     #current distance from the seed point
    node_best = None    #current candidate node    
    
    for node1 in graph: 
        #check if this is the node that best approximates seed point location
        dist_seed_this = math.sqrt((seedxy[0]-node_dict[node1].X)**2 + (seedxy[1]-node_dict[node1].Y)**2)
        if  dist_seed_this < dist_seed_best:
            dist_seed_best = dist_seed_this
            node_best = node1
        
        #create the edges that extend ahead of the current node
        NodeCheckRight(node_dict, graph, node1, xsize, nodecount)
        NodeCheckDownLeft(node_dict, graph, node1, xsize, nodecount)
        NodeCheckDown(node_dict, graph, node1, xsize, nodecount)
        NodeCheckDownRight(node_dict, graph, node1, xsize, nodecount)
    
    print ("Weighted graph in " + PrintTimeBenchmark(lasttime))
    lasttime = time.time()
    print ("Edges in initial representation: " + str(graph.number_of_edges()))
    
    #build initial tree from node_best
    treecount  = 0
    ConstructPartialTree(graph, node_dict, node_best, treecount)
    #find additional trees that were detached
    for key in node_dict:
        if key in graph:
            if len(graph[key]) == 8:
                treecount = ConstructPartialTree(graph, node_dict, key, treecount)
                
    print ("Added additional trees in " + PrintTimeBenchmark(lasttime))
    lasttime = time.time()    
    print("Total tree count: " + str(treecount))
        
    #We will probably need to add node_best to the return

    return node_dict 

def NodeCheckRight(node_dict, graph, node1, xsize, nodecount):
    node2x = node_dict[node1].X + 1
    node2y = node_dict[node1].Y
    NodeCheckingMechanism(node2x, node2y, node1, xsize, nodecount, node_dict, graph)

def NodeCheckDownLeft(node_dict, graph, node1, xsize, nodecount):
    node2x = node_dict[node1].X - 1
    node2y = node_dict[node1].Y + 1
    NodeCheckingMechanism(node2x, node2y, node1, xsize, nodecount, node_dict, graph)

def NodeCheckDown(node_dict, graph, node1, xsize, nodecount):
    node2x = node_dict[node1].X
    node2y = node_dict[node1].Y + 1
    NodeCheckingMechanism(node2x, node2y, node1, xsize, nodecount, node_dict, graph)
                
def NodeCheckDownRight(node_dict, graph, node1, xsize, nodecount):
    node2x = node_dict[node1].X + 1
    node2y = node_dict[node1].Y + 1
    NodeCheckingMechanism(node2x, node2y, node1, xsize, nodecount, node_dict, graph)
                
def NodeCheckingMechanism(node2x, node2y, node1, xsize, nodecount, node_dict, graph):
    for node2 in range(node1, MaxRange(node1, xsize, nodecount)):
        if (node_dict[node2].X == node2x):
            if (node_dict[node2].Y == node2y):
                weightval = CalculateWeight(node_dict[node1].Intensity, node_dict[node2].Intensity)
                graph.add_edge(node1, node2)
                graph[node1][node2]['weight'] = weightval
                break
                
def MaxRange(node1, maxsize, nodecount):
    #calculates the index within node_dict of the last possible node that could represent the pixel one down and one to
    #the right from the current node1. If the entire image is made of nodes, this index is node1 + the width of the
    #image + 2, for a complete line across the image plus the pixel below and below-right (the target)
    if (node1 + maxsize + 2) < (nodecount - 1):
        return (node1 + maxsize + 2)
    else:
        return (nodecount -1)    
    
def CalculateWeight(intensity1, intensity2):
    #formula taken from Peng et al section 2.2
    result1 = math.exp(10*(1-intensity1)**2)
    result2 = math.exp(10*(1-intensity2)**2)
    return (result1+result2)/2

def ConstructPartialTree(graph, node_dict, seed_node, treecount):
    pred_dict, distance_dict = nx.dijkstra_predecessor_and_distance(graph, seed_node)
    sig_tree = TreeCheck(pred_dict, node_dict)
    if sig_tree:
        treecount += 1
    # set parent/children relationships
    for key in pred_dict:
        if len(pred_dict[key]):
            if sig_tree:            
                node_dict[key].Parent = int(pred_dict[key][0])
                node_dict[int(pred_dict[key][0])].Children.append(key)
            graph.remove_node(key)
    return treecount
            
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
    if maxY > 2000:
        return False
    elif maxX - minX < 50:
        return False
    elif maxX - minX < 50:
        return False
    else:
        return (count>1500)
        
def PrintTimeBenchmark(lasttime):
    elapsed = time.time() - lasttime
    minutes = int(elapsed / 60)
    seconds = str(round((elapsed % 60), 2))
    minutes = str(minutes)
    return minutes + " minutes and " + seconds + " seconds."