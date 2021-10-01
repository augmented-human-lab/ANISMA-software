from tkinter import *
from render.RenderingObject import *
from util.drawUtil import *
from UIElements.Anchor import *

class Button(RenderingObject):
    _color_fill = "#225564"
    _color_fill_highlight = "#2D6B7F"
    _color_fill_active = "#1E4A5A"
    _color_outline = ""
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

    def getAnchorLocation(self):
        size = [self._canvas.winfo_width(), self._canvas.winfo_height()]

        if self._anchor == Anchor.TOPRIGHT:
            return [size[0]-self._location[0], self._location[1]]
        elif self._anchor == Anchor.TOPCENTER:
            return [size[0]/2+self._location[0], self._location[1]]
        elif self._anchor == Anchor.BOTTOMCENTER:
            return [size[0]/2+self._location[0], size[1]-self._location[1]]
        elif self._anchor == Anchor.BOTTOMLEFT:
            return [self._location[0], size[1]-self._location[1]]
        elif self._anchor == Anchor.BOTTOMRIGHT:
            return [size[0]-self._location[0], size[1]-self._location[1]]
        elif self._anchor == Anchor.CENTER:
            return [size[0]/2+self._location[0], size[1]/2+self._location[1]]
        else:
            return self._location

    def setLocation(self, x, y):
        self._location = [x, y]

    def setSize(self, width, height):
        self._width = width
        self._height = height

    def update(self):

        location = self.getAnchorLocation()

        if self.isHighlighted:
            roundPolygon(self._canvas, [location[0]-self._width/2, location[0]-self._width/2, location[0]+self._width/2, location[0]+self._width/2], [location[1]-self._height/2, location[1]+self._height/2, location[1]+self._height/2, location[1]-self._height/2], 8, width=0, outline=self._color_outline, fill=self._color_fill_highlight)
        else:
            if self._activated:
                roundPolygon(self._canvas, [location[0]-self._width/2, location[0]-self._width/2, location[0]+self._width/2, location[0]+self._width/2], [location[1]-self._height/2, location[1]+self._height/2, location[1]+self._height/2, location[1]-self._height/2], 8, width=0, outline=self._color_outline, fill=self._color_fill_active)
            else:
                roundPolygon(self._canvas, [location[0]-self._width/2, location[0]-self._width/2, location[0]+self._width/2, location[0]+self._width/2], [location[1]-self._height/2, location[1]+self._height/2, location[1]+self._height/2, location[1]-self._height/2], 8, width=0, outline=self._color_outline, fill=self._color_fill)

        self._canvas.create_text(location[0], location[1], anchor=CENTER, font=("Open Sans SemiBold", 18), fill="#FFFFFF", text=self._text)

    def renderAsActivated(self, active):
        self._activated = active

    def isActive(self):
        return self._activated
