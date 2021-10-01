from tkinter import *
from render.RenderingObject import *
from util.util import *

class Node(RenderingObject):

    def __init__(self, canvas, diameter=5):
        self._canvas = canvas
        self._connections = []
        self._location = [0,0]
        self._size = diameter
        self._id = 0


        self._color_fill_loose = "#B0BAC5"
        self._color_outline_loose = "#3F4A56"
        self._color_outline_loose_highlight = "#CCC"
        self._color_fill_loose_highlight = "#AAA"

        self._color_fill_default = "#9473FF"
        self._color_fill = "#9473FF"
        self._color_fill_highlight = "#8038EB"
        self._color_outline = "#3F4A56"
        self._color_outline_highlight = "#9473FF"


    def setCanvas(self, canvas):
        self._canvas = canvas

    def getLocation(self):
        return self._location

    def setLocation(self, x, y):
        self._location = [x, y]
        self._canvas.coords(self._id, self._location[0]-self._size, self._location[1]-self._size, self._location[0]+self._size, self._location[1]+self._size)
        self.requestUpdate(self._id)

    def update(self, zoomlevel):
        if self.isHighlighted:
            self._id = self._canvas.create_oval(self._location[0]-self._size, self._location[1]-self._size, self._location[0]+self._size, self._location[1]+self._size, fill=self._color_fill_highlight, outline=self._color_outline, width=1*zoomlevel)
        else:
            self._id = self._canvas.create_oval(self._location[0]-self._size, self._location[1]-self._size, self._location[0]+self._size, self._location[1]+self._size, fill=self._color_fill, outline=self._color_outline, width=1*zoomlevel)

    def isInBounds(self, x, y):
        return getDistance([x,y], self._location) <= self._size

    def getConnections(self):
        return self._connections

    def addConnection(self, conn):
        if conn not in self._connections:
            self._connections.append(conn)

    def removeConnection(self, conn):
        if conn in self._connections:
            self._connections.remove(conn)

    def setColor(self, color):
        self._color_fill = color

    def resetColor(self):
        self._color_fill = self._color_fill_default

    def getColor(self):
        return self._color_fill

    def replaceWith(self, newNode):
        for c in self._connections:
            c.replaceNode(self, newNode)
            newNode.addConnection(c)

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['_canvas']
        del state['_id']
        return state
