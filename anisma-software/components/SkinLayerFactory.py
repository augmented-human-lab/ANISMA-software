from components.SkinNode import SkinNode
from components.SkinSpring import SkinSpring
from components.SkinLayer import SkinLayer
from util.util import *
import random

def createSkinNode(inView, atLocation, withSpringLength):
    node = SkinNode(inView.getCanvas(), withSpringLength)
    inView.add(node)
    node.setLocation(atLocation[0], atLocation[1])
    return node

def createSkinSpring(inView, nodeA, nodeB):
    conn = SkinSpring(inView.getCanvas(), nodeA, nodeB)
    inView.add(conn)
    return conn

def createNewSkinLayer(view, startLocation, endLocation, springRestingLength):
    skinLayer = SkinLayer()

    xnodenum = int((endLocation[0] - startLocation[0]) / springRestingLength + 1)
    ynodenum = int((endLocation[1] - startLocation[1]) / springRestingLength + 1)
    nodemap = [[None for i in range(xnodenum)] for j in range(ynodenum)]

    prestretch = 1.1

    for i in range(xnodenum):
        for j in range(ynodenum):
            rx = 0
            ry = 0
            location = [startLocation[0]+i*springRestingLength+rx, startLocation[1]+j*springRestingLength+ry]
            node = createSkinNode(view, location, springRestingLength)
            nodemap[i][j] = node
            skinLayer.addSkinNode(node)

            if i > 0:
                # add horizontal spring
                spring = createSkinSpring(view, node, nodemap[i-1][j])
                spring.setRestingLength(springRestingLength/prestretch)
                skinLayer.addSkinSpring(spring)

            if j > 0:
                # add vertical spring
                spring = createSkinSpring(view, node, nodemap[i][j-1])
                spring.setRestingLength(springRestingLength/prestretch)
                skinLayer.addSkinSpring(spring)

            if i > 0 and j > 0:
                # add diagonal spring
                spring = createSkinSpring(view, node, nodemap[i-1][j-1])
                length = getDistance(node.getLocation(), nodemap[i-1][j-1].getLocation())
                spring.setRestingLength(length/prestretch)
                spring.setDiagonal(True)
                skinLayer.addSkinSpring(spring)

                spring = createSkinSpring(view, nodemap[i-1][j], nodemap[i][j-1])
                length = getDistance(nodemap[i-1][j].getLocation(), nodemap[i][j-1].getLocation())
                spring.setRestingLength(length/prestretch)
                spring.setDiagonal(True)
                skinLayer.addSkinSpring(spring)

    skinLayer.randomize()
    return skinLayer
