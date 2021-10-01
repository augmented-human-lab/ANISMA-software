from tkinter import *
from render.RenderingObject import *
from util.util import *

class UIScale(RenderingObject):

    _length = 20
    _color = "#8091A5"

    def __init__(self, canvas, location):
        self._canvas = canvas
        self.location = location

    def setLocation(self, location):
        self.location = location

    def update(self, zoomlevel):
        size = [self._canvas.winfo_width(), self._canvas.winfo_height()]
        location = [self._canvas.canvasx(self.location[0])/zoomlevel, self._canvas.canvasy(size[1]-self.location[1])/zoomlevel]

        self._canvas.create_line(location[0], location[1], location[0]+self._length, location[1], fill=self._color, width=1, joinstyle=ROUND, capstyle=ROUND)
        self._canvas.create_line(location[0], location[1], location[0], location[1] - 2, fill=self._color, width=1, joinstyle=ROUND, capstyle=ROUND)
        self._canvas.create_line(location[0]+5, location[1], location[0]+5, location[1] - 1, fill=self._color, width=1, joinstyle=ROUND, capstyle=ROUND)
        self._canvas.create_line(location[0]+10, location[1], location[0]+10, location[1] - 2, fill=self._color, width=1, joinstyle=ROUND, capstyle=ROUND)
        self._canvas.create_line(location[0]+15, location[1], location[0]+15, location[1] - 1, fill=self._color, width=1, joinstyle=ROUND, capstyle=ROUND)
        self._canvas.create_line(location[0]+20, location[1], location[0]+20, location[1] - 2, fill=self._color, width=1, joinstyle=ROUND, capstyle=ROUND)

        sText1 = '0'
        sText2 = '10'
        sText3 = '20'
        sTextUnit = 'mm'
        font = ("Verdana", 8)
        self._canvas.create_text(location[0]-0.5, location[1]-6, anchor=W, font=font, text=sText1)
        self._canvas.create_text(location[0]+10-2, location[1]-6, anchor=W, font=font, text=sText2)
        self._canvas.create_text(location[0]+20-2, location[1]-6, anchor=W, font=font, text=sText3)
        self._canvas.create_text(location[0], location[1]+2, anchor=W, font=font, text=sTextUnit)

    def isInBounds(self, x, y):
        return False
