from tkinter import *
import tkinter.font as tkFont
from render.RenderingObject import *
from util.util import *
from util.drawUtil import *

class Legend(RenderingObject):

    _length = 20
    _color = "#AAA"


    _color_fill_default = "#AAA"
    _color_fill = "#AAA"
    _color_fill_highlight = "#EEE"
    _color_outline = "#DDD"

    def __init__(self, canvas, location):
        self._canvas = canvas
        self.location = location

    def setLocation(self, location):
        self.location = location

    def update(self, zoomlevel):
        zoomX = zoomlevel
        zoomY = zoomlevel
        size = [self._canvas.winfo_width(), self._canvas.winfo_height()]
        location = [self._canvas.canvasx(self.location[0])/zoomX, self._canvas.canvasy(size[1]-self.location[1])/zoomY]

        sTextUnit = 'mm'
        fontTitle = ("Verdana", 14, 'bold')
        font = tkFont.Font(family="Verdana", size=12, weight="normal")

        nodesize = 16 / 2 / zoomlevel

        # Draw legend title
        self._canvas.create_text(location[0]-1/zoomX, location[1]-6/zoomY, anchor=W, font=fontTitle, text="Legend", fill="#12333D")

        # Draw Node - type solid
        location[1] += 25 / zoomY

        self._canvas.create_text(location[0]+24/zoomX, location[1], anchor=W, font=font, text="Skin Attached Node", fill="#12333D")
        roundPolygon(self._canvas, [location[0] + nodesize - nodesize, location[0] + nodesize-nodesize, location[0] + nodesize +nodesize, location[0] + nodesize +nodesize], [location[1]-nodesize, location[1]+nodesize, location[1]+nodesize, location[1]-nodesize], 2, width=2, outline="#12333D", fill="#9473FF")

        # Draw Node - type loose
        location[1] += 30 / zoomY
        self._canvas.create_text(location[0]+24/zoomX, location[1], anchor=W, font=font, text="Skin Detached Node", fill="#12333D")
        self._canvas.create_oval(nodesize + location[0]-nodesize, location[1]-nodesize, nodesize + location[0]+nodesize, location[1]+nodesize, fill="#B0BAC5", outline="#12333D", width=2)

        # Draw SMA Connection
        location[1] += 30 / zoomY
        self._canvas.create_text(location[0]+24/zoomX, location[1], anchor=W, font=font, text="SMA Spring", fill="#12333D")
        drawConnection(self._canvas, location, [location[0]+nodesize*2, location[1]], 2, 6 / zoomlevel, width=2, color="#3F4A56")

        # Draw Rigid Area
        location[1] += 30 / zoomY
        self._canvas.create_text(location[0]+24/zoomX, location[1], anchor=W, font=font, text="Rigid Area", fill="#12333D")
        roundPolygon(self._canvas, [location[0] + nodesize - nodesize, location[0] + nodesize-nodesize, location[0] + nodesize +nodesize, location[0] + nodesize +nodesize], [location[1]-nodesize, location[1]+nodesize, location[1]+nodesize, location[1]-nodesize], 2, width=0, outline="", fill="#3BA4FF")

        # Draw EMA
        location[1] += 30 / zoomY
        self._canvas.create_text(location[0]+24/zoomX, location[1], anchor=W, font=font, text="Effective Area", fill="#12333D")
        roundPolygon(self._canvas, [location[0] + nodesize - nodesize, location[0] + nodesize-nodesize, location[0] + nodesize +nodesize, location[0] + nodesize +nodesize], [location[1]-nodesize, location[1]+nodesize, location[1]+nodesize, location[1]-nodesize], 2, width=0, outline="", fill="#4FD7CF")

    def isInBounds(self, x, y):
        return False
