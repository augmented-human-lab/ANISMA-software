from tkinter import *
from util.drawUtil import *
from UIElements.Button import Button

class ToolBoxItem(Button):

    def __init__(self, canvas, text, callback=None, ic=None):
        super().__init__(canvas, [0,0], 0, 0, text, callback=callback, ic=ic)
        self._infoCanvas = None

    def setInfoCanvas(self, canvas):
        self._infoCanvas = canvas

    def update(self):
        location = self.getAnchorLocation()
        padding = 10
        if self.isHighlighted:
            self._canvas.create_rectangle(location[0]-self._width/2, location[1]-self._height/2, location[0]+self._width/2, location[1]+self._height/2, width=1, outline=self._color_outline, fill=self._color_fill_highlight)
        else:
            if self._activated:
                self._canvas.create_rectangle(location[0]-self._width/2, location[1]-self._height/2, location[0]+self._width/2, location[1]+self._height/2, width=1, outline=self._color_outline, fill=self._color_fill_active)
            else:
                self._canvas.create_rectangle(location[0]-self._width/2, location[1]-self._height/2, location[0]+self._width/2, location[1]+self._height/2, width=1, outline=self._color_outline, fill=self._color_fill)

        self._canvas.create_text(location[0]-self._width/2+padding, location[1]-self._height/2+padding, anchor=NW, font="Verdana", text=self._text)
