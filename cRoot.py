 #-*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   file=       cRoot
#   author=     Zackery Keith 
#   date=       Nov 6 2014
#   purpose=    classes to describe a root or subroot object
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Library import declarations
import math

# Function import declarations

# Class declaration
class Root:
     
    # Nodes: dictionary with:
    #   Keys: int representing the node's position 0 <= key < n
    #   Values: tuple of a node object and the distance to the next node
    Nodes = {}
    
    # Children: dictionary with:
    #   Keys: int representing the child's position in Nodes
    #   Values: Root object representing the child
    Children = {}
    
    # Parent: tuple with:
    #   Value0: Root object representing the parent root
    #   Value1: int representing this root's position in the parent's Nodes
    Parent = ()
    
    # Loads a list structure of Node objects into the root
    # Assumes the nodes are in order
    def LoadNodes(self, nodelist):
        for node in nodelist:
            self.Nodes[len(self.Nodes)] = (node, 0)
        self.UpdateDistances()
            
    # Updates the distances between nodes in the Nodes dictionary
    def UpdateDistances(self):
        for key in self.Nodes:
            thisNode = self.Nodes[key][0]
            if key+1 < len(self.Nodes):
                nextNode = self.Nodes[key+1][0]
                deltaX = thisNode.X - nextNode.X
                deltaY = thisNode.Y - nextNode.Y
                distance = math.sqrt(deltaX**2 + deltaY**2)
            else:
                distance = 0
            #change the item associated with the current key to include new distance
            self.Nodes[key] = (thisNode, distance)
    
    # Adds a child root to this at a given position
    # Also sets this as the parent of the child root
    def SetChild(self, childroot, position):
        self.Children[position] = childroot
        childroot.Parent = (self, position)

    # Gets and sums the lengths between each node in the root        
    def GetRootLength(self):
        totalLength = 0
        for key in self.Nodes:
            #add the length associated with this node
            totalLength += self.Nodes[key][1]  
        return totalLength

class Node:
    
    # X location of the node
    X = -1
    
    # Y location of the node
    Y = -1
    
    # Intensity of the root at this node
    Intensity = -1

    # Radius of the root at this node
    Radius = -1    
    
    # Parent of this node (none means this is the root of the tree)
    Parent = None
    
    # Children of this node (if empty, this is a leaf node)
    Children = None
    
    # Expects ' newNode = Node(xLocation, yLocation, intensity) '
    def __init__(self, x, y, i):
        self.X = x
        self.Y = y
        self.Intensity = i
        self.Children = list()