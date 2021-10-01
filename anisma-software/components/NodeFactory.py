from components.Node import Node
from components.SMANode import SMANode
from components.SMASpringParameters import *
from components.SMANodeType import *

nodeNum = 0

def createNode(inView, atLocation):
    node = Node(inView.getCanvas())
    inView.add(node)
    node.setLocation(atLocation[0], atLocation[1])
    return node

def createSMANode(inView, atLocation, type=SMANodeType.ELASTIC):
    global nodeNum
    node = SMANode(inView.getCanvas(), type=type)
    node.setPin(nodeNum)
    nodeNum += 1
    inView.add(node)
    node.setLocation(atLocation[0], atLocation[1])

    return node