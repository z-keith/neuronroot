 #-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       fPruneOCR
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    Removes redundant nodes from an OCR
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import config

# Class import declarations

# Function import declarations

def PruneOCR(node_dict):
    node_dict = RemoveDark(node_dict)

    print ("Removed dark leaves in " + config.PrintTimeBenchmark())
    print ("Removed " + str(config.initial_nodecount - len(node_dict)) + " dark nodes.")

    nodecount = len(node_dict)
    node_dict = RemoveRedundant(node_dict)

    print ("Removed redundant nodes in " + config.PrintTimeBenchmark())
    print ("Removed " + str(nodecount - len(node_dict)) + " redundant nodes.")

    print("Total nodes in final representation: " + str(len(node_dict)))
    print("Compression: " + str(round(100*(1 - len(node_dict)/config.initial_nodecount), 1)) + "%")

    return node_dict

def RemoveDark(node_dict):
    whiteleaves = False
    while not whiteleaves:
        leafset = []
        removeset = []

        for key in node_dict:
            if not node_dict[key].Children:
                if not node_dict[key].Parent:
                    removeset.append(key)
                else:
                    leafset.append(key)

        for node in removeset:
            RemoveNode(node_dict, node)

        allwhite = True
        for node in leafset:
            if node_dict[node].Intensity < 0.12:
                RemoveNode(node_dict, node)
                allwhite = False
        if allwhite:
            whiteleaves = True

    return node_dict

def RemoveRedundant(node_dict):

    return node_dict

def RemoveNode(node_dict, node):
    if node in node_dict:
        if node_dict[node].Children:
            for child in node_dict[node].Children:
                node_dict[child].Parent = node_dict[node].Parent
        if node_dict[node].Parent:
            node_dict[node_dict[node].Parent].Children.remove(node)
        del node_dict[node]