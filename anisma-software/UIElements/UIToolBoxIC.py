from UIElements.Button import *
from UIElements.ToolBoxItems.TBISMAModule import TBISMAModule
import time

class UIToolBoxIC():

    def __init__(self, window, canvas, uiview, mainView):
        self.__window = window
        self._canvas = canvas
        self._uiview = uiview
        self._mainView = mainView

        self.__mousePoint = [0,0]
        self.__hoveredObject = None
        self._canvas.bind("<ButtonPress-1>", self.onMousePressedOnView)
        self._canvas.bind("<ButtonRelease-1>", self.onMouseReleasedOnView)
        self._canvas.bind("<Motion>", self.onMouseMovedOnView)
        self._canvas.bind("<B1-Motion>", self.onMouseDragOnView)
        self._canvas.bind("<Enter>", self.onMouseEnter)
        self._canvas.bind("<Leave>", self.onMouseLeave)

    def getView(self):
        return self._uiview

    def onMouseMovedOnView(self, event=None):
        self.__mousePoint = [event.x,event.y]

        ## Highlight hovered component
        # un highlight last
        if self.__hoveredObject is not None:
            self.__hoveredObject.isHighlighted = False

        # find closest component
        obj = self._uiview.findClosest(self.__mousePoint)
        self._uiview.setInfoBoxObj(None)

        # if found one highlight it
        if obj is not None:
            obj.isHighlighted = True
        else:
            self.__window.config(cursor="")

        self.__hoveredObject = obj
        self._uiview.updateView()


    def onMousePressedOnView(self, event=None):
        if isinstance(self.__hoveredObject, Button):
            self.__hoveredObject.onClick()
        self._uiview.updateView()

    def onMouseReleasedOnView(self, event=None):
        self._uiview.updateView()

    def onMouseDragOnView(self, event=None):
        self.__mousePoint = [event.x,event.y]
        self._uiview.updateView()

    def onMouseEnter(self, event=None):
        self._uiview.updateView()

    def onMouseLeave(self, event=None):
        if self.__hoveredObject is not None:
            self.__hoveredObject.isHighlighted = False
        self._uiview.updateView()
