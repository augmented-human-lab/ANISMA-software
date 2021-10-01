from tkinter import *
from components.Connection import Connection
from util.util import *

class UIView:
    __windowWidth = 0
    __windowHeight = 0

    def __init__(self, canvas):
        self.__canvas = canvas
        canvas.bind("<Configure>", self.__onResize)
        self._objects = []
        self._projectName = "Untitled_File"

    def __onResize(self, event):
        self.__windowWidth = event.width*0
        self.__windowHeight = event.height*0

        self.updateView()

    def updateView(self, noDelete=False):
        if not noDelete:
            self.__canvas.delete("all")

        for o in self._objects:
            o.update()

        self.__canvas.pack()

    def add(self, obj):
        # consider Z-ordering
        # ensure putting connections before nodes
        if isinstance(obj, Connection):
            self._objects.insert(1,obj) # grid/background first
        else:
            self._objects.append(obj)

        obj.setView(self)

    def remove(self, obj):
        self._objects.remove(obj)

    def getCanvas(self):
        return self.__canvas

    # Finds the object closest object of any or a certain type
    def findClosest(self, location, ofType=None, excluding=None):
        for o in reversed(self._objects): # loop through inverse to select top most visible objects first
            if (ofType is None) or ((ofType is not None) and isinstance(o, ofType)) and o is not excluding:
                if o.isInBounds(location[0], location[1]):
                    return o

        return None
