from tkinter import *
from render.RenderingObject import *
from util.util import *

class Connection(RenderingObject):
    _nodes = []
    __id = 0
    _color = "#DDD"
    _color_highlighted = "#EEE"

    def __init__(self, canvas, nodeA, nodeB, width=7):
        self._canvas = canvas
        self.__width = width
        self.setNodes(nodeA, nodeB)

    def setNodes(self, nodeA, nodeB):
        self.unlinkNodes()
        self._nodes = []
        self._nodes.append(nodeA)
        self._nodes.append(nodeB)

        nodeA.addConnection(self)
        nodeB.addConnection(self)

    def setCanvas(self, canvas):
        self._canvas = canvas

    def unlinkNodes(self):
        for n in self._nodes:
            n.removeConnection(self)

    def update(self, zoomlevel):
        startLocation = self._nodes[0].getLocation()
        endLocation = self._nodes[1].getLocation()

        if self.isHighlighted:
            self.__id = self._canvas.create_line(startLocation[0], startLocation[1], endLocation[0], endLocation[1], fill=self._color_highlighted, width=self.__width*zoomlevel, joinstyle=ROUND, capstyle=ROUND)
        else:
            self.__id = self._canvas.create_line(startLocation[0], startLocation[1], endLocation[0], endLocation[1], fill=self._color, width=self.__width*zoomlevel, joinstyle=ROUND, capstyle=ROUND)

    def isInBounds(self, x, y):
        # get angle between horizontal and connection line
        nodePosA = self._nodes[0].getLocation()
        nodePosB = self._nodes[1].getLocation()

        vec = [nodePosB[0] - nodePosA[0], nodePosB[1] - nodePosA[1]]
        horizVec = [1, 0]

        angle = angleBetween(vec, horizVec)

        # rotate the point [x, y] by the derived vector
        p = rotatePoint(x - nodePosA[0], y - nodePosA[1], angle, clockwise=(nodePosA[1]>nodePosB[1]))

        # check if rotated point lies in horizontally aligned rect bounds
        dist = getDistance(nodePosA, nodePosB)
        if p[0] >= 0 and p[0] <= dist:
            if abs(p[1]) <= self.__width / 2:
                return True

        return False

    def getNodes(self):
        return self._nodes

    def getOtherNode(self, notThisNode):
        for n in self._nodes:
            if n is not notThisNode:
                return n

    def replaceNode(self, replaceA, withB):
        conns = replaceA.getConnections()

        if self._nodes[0] is replaceA:
            #self._nodes[0].removeConnection(self)
            self._nodes[0] = withB

        elif self._nodes[1] is replaceA:
            #self._nodes[1].removeConnection(self)
            self._nodes[1] = withB

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['_canvas']
        return state
