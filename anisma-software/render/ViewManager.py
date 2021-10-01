from tkinter import *
from components.Connection import Connection
from components.SMAConnection import SMAConnection
from components.Node import Node
from components.SMANode import SMANode
from util.util import *

class ViewManager:
    __zoom = 4.0
    __zoom_max = 6.0
    __zoom_min = 1.5
    __windowWidth = 0
    __windowHeight = 0
    __panning = True
    __zooming = True

    def __init__(self, canvas, initialViewPos):
        self.__canvas = canvas
        canvas.bind("<Configure>", self.__onResize)
        canvas.bind("<MouseWheel>", self.do_zoom)
        self.__objects = []

        # initially drag to center
        self.__canvas.scan_mark(0, 0)
        self.__canvas.scan_dragto(-initialViewPos[0], -initialViewPos[1], gain=1)
        self._scene = None
        self._controllerBoardActive = False
        self._designError = False

        self._gridVal = BooleanVar()
        self._gridcb = Checkbutton(self.__canvas, text="Grid", anchor=CENTER, background="#F3F5F9", variable=self._gridVal, command=self.cb_grid_click, onvalue = True, offvalue = False)
        self._gridcb.place(x=29, y=350)

    def cb_grid_click(self):
        print("grid activated", self._gridVal.get())

    def setGridActivated(self, val):
        self._gridVal.set(val)

    def isGridActivated(self):
        return self._gridVal.get()

    def showGrid(self, show):
        if show:
            self._gridcb.place(x=29, y=350)
        else:
            self._gridcb.place_forget()

    def setScene(self, scene):
        self._scene = scene

    def do_prePan(self, event):
        if self.__panning:
            self.__canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):

        if self.__panning:
            self.__canvas.scan_dragto(event.x, event.y, gain=1)

    def do_zoom(self, event):

        mloc = [self.__canvas.canvasx(event.x)/self.__zoom, self.__canvas.canvasy(event.y)/self.__zoom]

        if self.__zooming:
            factor = 1.01 ** event.delta
            self.__zoom *= factor
            if self.__zoom < self.__zoom_min:
                self.__zoom = self.__zoom_min
            elif self.__zoom > self.__zoom_max:
                self.__zoom = self.__zoom_max

            self.updateView()


    def __onResize(self, event):
        self.__windowWidth = event.width*0
        self.__windowHeight = event.height*0

        self.updateView()

    def update(self, objID):
        self.__canvas.scale(objID, self.__windowWidth / 2.0, self.__windowHeight / 2.0, self.__zoom, self.__zoom)

    def setControllerBoardActive(self, enabled):
        self._controllerBoardActive = enabled

    def updateView(self):
        foundError = False
        self.__canvas.delete("all")

        for o in self.__objects:
            o.update(self.__zoom)
            if isinstance(o, SMAConnection):
                if o.hasError():
                    foundError = True

        self._designError = foundError

        for i in range(10):
            tagname = "level-" + str(9-i)
            self.__canvas.lower(tagname)

        self.__canvas.lower("background")
        self.__canvas.scale(ALL, self.__windowWidth / 2.0, self.__windowHeight / 2.0, self.__zoom, self.__zoom)
        self.__canvas.pack()

        if self._controllerBoardActive:
            self.__canvas.create_text(self.__canvas.canvasx(self.__canvas.winfo_width()/2), self.__canvas.canvasy(80), anchor=CENTER, font=("Verdana", 30), text="Replaying with Controllerboard", fill="#FF006E")

        self.__canvas.update_idletasks

    def add(self, obj):
        # consider Z-ordering
        # ensure putting connections before nodes

        if isinstance(obj, SMAConnection):
            if self._scene is not None:
                self._scene.addTrackForSMA(obj)

        if isinstance(obj, Connection):
            self.__objects.insert(2,obj) # grid/background first
        else:
            self.__objects.append(obj)

        obj.setView(self)

    def remove(self, obj, recurse=True, update=True, deleteConnections=False):
        # If a node has to be deleted then..
        if recurse:
            if isinstance(obj, Node):
                # remove all connections too.
                conns = obj.getConnections().copy()
                for c in conns:
                    if c in self.__objects:
                        self.remove(c, update=update, recurse=recurse, deleteConnections=deleteConnections)

            if isinstance(obj, Connection):
                # if we delete a connection we should unlink the attached nodes
                nodes = obj.getNodes().copy()
                obj.unlinkNodes()

                # delete left nodes which have no connections
                for n in nodes:
                    if len(n.getConnections()) < 1:
                        self.remove(n, update=update, recurse=recurse, deleteConnections=deleteConnections)

        if obj in self.__objects:
            if isinstance(obj, SMAConnection):
                if self._scene is not None:
                    self._scene.removeTrackForSMA(obj)

            self.__objects.remove(obj)
            if isinstance(obj, Connection):
                obj.unlinkNodes()
            if isinstance(obj, Node):
                if deleteConnections:
                    conns = obj.getConnections().copy()
                    for c in conns:
                        if c in self.__objects:
                            self.remove(c, update=update, recurse=recurse, deleteConnections=deleteConnections)

    def removeClipsForSMA(self, sma):
        self._scene.removeClipsForSMA(sma)

    def getZoom(self):
        return self.__zoom

    def getCanvas(self):
        return self.__canvas

    def setZooming(self, enabled):
        self.__zooming = enabled

    def setPanning(self, enabled):
        self.__panning = enabled

    def getAllObjects(self):
        return self.__objects

    def getAllNonPersistantObjects(self):
        nonpersistant = []

        for o in self.__objects:
            if isinstance(o, SMANode) or isinstance(o, SMAConnection):
                nonpersistant.append(o)

        return nonpersistant

    def connectionExists(self, nodeA, nodeB):
        for o in self.__objects:
            if isinstance(o, Connection):
                A = o.getNodes()[0]
                B = o.getNodes()[1]

                if (nodeA == A and nodeB == B) or (nodeA == B and nodeB == A):
                    return True

        return False

    # Finds the object closest object of any or a certain type
    def findClosest(self, location, ofType=None, excluding=None):
        for o in reversed(self.__objects): # loop through inverse to select top most visible objects first
            if (ofType is None) or ((ofType is not None) and isinstance(o, ofType)) and o is not excluding:
                if o.isInBounds(location[0], location[1]):
                    return o

        return None

    def foundError(self):
        return self._designError
