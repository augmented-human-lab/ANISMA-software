from tkinter import *
from render.RenderingObject import *
from util.drawUtil import *
from UIElements.Anchor import *
from UIElements.Button import Button


class TabBarButton(Button):
    _color_fill = "#FFFFFF"
    _color_fill_highlight = "#F0F1F5"
    _color_fill_active = "#152F39"
    _color_outline = "#152F39"
    _activated = False

    def __init__(self, canvas, location, width, height, text, callback=None, ic=None, radioGroup=None, anchor=Anchor.TOPLEFT):
        self._canvas = canvas
        self._text = text
        self._width = width
        self._height = height
        self._location = location
        self._callback = callback
        self._ic = ic
        self._radioBtnGrp = None
        self._anchor = anchor

        if radioGroup is not None:
            self.setRadioGroup(radioGroup)

    def setRadioGroup(self, group):
        self._radioBtnGrp = group
        self._radioBtnGrp.addButton(self)

    def onClick(self):
        if self._radioBtnGrp is not None:
            self._radioBtnGrp.setActive(button=self)
        self._callback(self, self._ic)

    def setText(self, text):
        self._text = text

    def isInBounds(self, x, y):
        location = self.getAnchorLocation()
        return  (x >= location[0]-self._width/2) and (x <= location[0]+self._width/2) and (y >= location[1]-self._height/2) and (y <= location[1]+self._height/2)

    def setLocation(self, x, y):
        self._location = [x, y]

    def setSize(self, width, height):
        self._width = width
        self._height = height

    def update(self):

        self._canvas.delete("topbarbutton"+str(self))
        location = self.getAnchorLocation()

        if self._activated:
            roundPolygon(self._canvas, [location[0]-self._width/2, location[0]-self._width/2, location[0]+self._width/2, location[0]+self._width/2], [location[1]-self._height/2, location[1]+self._height/2, location[1]+self._height/2, location[1]-self._height/2], 10, width=2, outline=self._color_outline, fill=self._color_fill_active, tags="topbarbuttons")
            self._canvas.create_text(location[0], location[1], anchor=CENTER, font=("Open Sans SemiBold", 18), fill="#FFFFFF", text=self._text, tags="topbarbuttons")
        else:
            if self.isHighlighted:
                roundPolygon(self._canvas, [location[0]-self._width/2, location[0]-self._width/2, location[0]+self._width/2, location[0]+self._width/2], [location[1]-self._height/2, location[1]+self._height/2, location[1]+self._height/2, location[1]-self._height/2], 10, width=2, outline=self._color_outline, fill=self._color_fill_highlight, tags="topbarbuttons")
                self._canvas.create_text(location[0], location[1], anchor=CENTER, font=("Open Sans SemiBold", 18), fill="#152F39", text=self._text, tags="topbarbuttons")
            else:
                roundPolygon(self._canvas, [location[0]-self._width/2, location[0]-self._width/2, location[0]+self._width/2, location[0]+self._width/2], [location[1]-self._height/2, location[1]+self._height/2, location[1]+self._height/2, location[1]-self._height/2], 10, width=2, outline=self._color_outline, fill=self._color_fill, tags="topbarbuttons")
                self._canvas.create_text(location[0], location[1], anchor=CENTER, font=("Open Sans SemiBold", 18), fill="#152F39", text=self._text, tags="topbarbuttons")

    def renderAsActivated(self, active):
        self._activated = active
