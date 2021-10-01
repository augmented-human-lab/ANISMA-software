from tkinter import *
from components.Connection import Connection
from util.util import *

class UIViewTopBar:
    __windowWidth = 0
    __windowHeight = 0

    def __init__(self, canvas):
        self.__canvas = canvas
        canvas.bind("<Configure>", self.__onResize)
        self.__objects = []
        self._projectName = "Untitled"

    def setProjectName(self, name):
        self._projectName = name

    def __onResize(self, event):
        self.__windowWidth = event.width*0
        self.__windowHeight = event.height*0

        self.updateView()

    def updateView(self, noDelete=False):
        if not noDelete:
            self.__canvas.delete("all")

        size = [self.__canvas.winfo_width(), self.__canvas.winfo_height()]
        self.__canvas.create_rectangle(0, size[1]-48, size[0], size[1], width=0, fill="#DFE6EE")
        self.__canvas.create_rectangle(size[0]/2 - (721-552)/2, 80, size[0]/2 + (721-552)/2, 80+30, width=2, fill="#12333D", outline="#12333D")
        self.__canvas.create_line(0, size[1]-1, size[0], size[1]-1, width=1, fill="#8091A5")

        # filename
        self.__canvas.create_text(size[0]/2, 24+24/2, anchor=CENTER, font=("Open Sans SemiBold", 18), fill="#FFFFFF", text=self._projectName)

        for o in self.__objects:
            o.update()

        self.__canvas.pack()

    def add(self, obj):
        # consider Z-ordering
        # ensure putting connections before nodes
        if isinstance(obj, Connection):
            self.__objects.insert(1,obj) # grid/background first
        else:
            self.__objects.append(obj)

        obj.setView(self)

    def remove(self, obj):
        self.__objects.remove(obj)

    def getCanvas(self):
        return self.__canvas

    # Finds the object closest object of any or a certain type
    def findClosest(self, location, ofType=None, excluding=None):
        for o in reversed(self.__objects): # loop through inverse to select top most visible objects first
            if (ofType is None) or ((ofType is not None) and isinstance(o, ofType)) and o is not excluding:
                if o.isInBounds(location[0], location[1]):
                    return o

        return None
