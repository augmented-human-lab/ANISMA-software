from tkinter import *
from render.RenderingObject import *

class TextField(RenderingObject):

    def __init__(self, view, location, width, height, title):
        self._parent = view.getCanvas()
        self._view = view
        self._location = location
        self._tfCanvas = Canvas(self._parent, width=width, height=100, bd=0, highlightthickness=0)
        self._width = width
        self._height = height
        self._buttonHeight = buttonHeight
        self._title = title

        self._tfCanvas.bind("<Motion>", self.onMouseMoved)
        self._tfCanvas.bind("<ButtonPress-1>", self.onMousePressed)
        self._tfCanvas.bind("<Leave>", self.onMouseLeave)
        self._hidden = False
        self._buttons = []

    def isInBounds(self, x, y):
        return False

    def update(self, zoomlevel):
        if not self._hidden:
            title_height = self._title_height = 25

            font = ("Verdana", 12)
            bold_font = ("Verdana", 12, "bold")
            self._tfCanvas.create_rectangle(0, 0, self._width-1, self._height, fill='#EEEEEE', outline='#CCCCCC', width=1)
            self._tfCanvas.create_text(self._width/2.0-3.8*len(self._title), title_height/2.0, anchor=W, font=bold_font, text=self._title)

            self._tfCanvas.place(x=self._location[0], y=self._location[1], height=self._height)

    def getCanvas(self):
        return self._tfCanvas

    def onMouseMoved(self, event=None):
        if event.y > self._title_height and event.y < self._title_height + len(self._buttons)*self._buttonHeight:
            self._hoveredButton = int( (event.y - self._title_height) / self._buttonHeight )
        else:
            self._hoveredButton = -1
        self.update(0)

    def onMousePressed(self, event=None):
        if event.y > self._title_height and event.y < self._title_height + len(self._buttons)*self._buttonHeight:
            self._hoveredButton = int( (event.y - self._title_height) / self._buttonHeight )
            self._buttons[self._hoveredButton].onClick()
            self.remove()

    def onMouseReleased(self, event=None):
        return

    def onMouseLeave(self, event=None):
        self._hoveredButton = -1
        self.update(0)

    def hide(self):
        self._tfCanvas.place_forget()
        self._hidden = True

    def remove(self):
        self.hide()
        self._view.remove(self)

    def showAt(self, location):
        self._location = location
        self._hidden = False
        self.update(0)
