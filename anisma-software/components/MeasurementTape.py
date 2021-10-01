from tkinter import *
from render.RenderingObject import *
from util.util import *

class MeasurementTape(RenderingObject):

    _length = 20
    _color = "#AAA"

    def __init__(self, canvas, startPoint, endPoint):
        self._canvas = canvas
        self._startPoint = startPoint
        self._endPoint = endPoint
        self._hidden = False
        self._cursorPos = [0, 0]
        self._drawCursor = False

    def setLocation(self, startPoint, endPoint):
        self._startPoint = startPoint
        self._endPoint = endPoint

    def setStartLocation(self, startPoint):
        self._startPoint = startPoint
        self._drawCursor = False

    def setEndLocation(self, endPoint):
        self._endPoint = endPoint
        self._drawCursor = False

    def show(self, enabled):
        self._hidden = not enabled
        self._drawCursor = False

    def drawCursorAt(self, pos):
        self._cursorPos = pos
        self._drawCursor = True

    def update(self, zoomlevel):
        if self._drawCursor:
            size = 1
            location = self._cursorPos
            self._canvas.create_oval(location[0]-size, location[1]-size, location[0]+size, location[1]+size, fill=self._color, width=0)
        if not self._hidden:
            size = [self._canvas.winfo_width(), self._canvas.winfo_height()]
            location = [self._canvas.canvasx(size[0]-120)/zoomlevel, self._canvas.canvasy(size[1]-40-150)/zoomlevel]
            self._canvas.create_line(self._startPoint[0], self._startPoint[1], self._endPoint[0], self._endPoint[1], fill=self._color, width=zoomlevel, joinstyle=ROUND, capstyle=ROUND)
            ddir = getUnitVec([self._endPoint[0]-self._startPoint[0], self._endPoint[1]-self._startPoint[1]])
            norm = [-ddir[1], ddir[0]]

            # draw tails
            taillength = 2.5
            lowtailstart = [self._startPoint[0]-norm[0]*taillength, self._startPoint[1]-norm[1]*taillength]
            lowtailend = [self._startPoint[0]+norm[0]*taillength, self._startPoint[1]+norm[1]*taillength]
            hightailstart = [self._endPoint[0]-norm[0]*taillength, self._endPoint[1]-norm[1]*taillength]
            hightailend = [self._endPoint[0]+norm[0]*taillength, self._endPoint[1]+norm[1]*taillength]
            self._canvas.create_line(lowtailstart[0], lowtailstart[1], lowtailend[0], lowtailend[1], fill=self._color, width=zoomlevel, joinstyle=ROUND, capstyle=ROUND)
            self._canvas.create_line(hightailstart[0], hightailstart[1], hightailend[0], hightailend[1], fill=self._color, width=zoomlevel, joinstyle=ROUND, capstyle=ROUND)

            # display distance
            dist = getDistance(self._startPoint, self._endPoint)
            sText1 = str(round(dist, 2)) + "mm"
            sTextUnit = 'mm'
            font = ("Verdana", int(3*zoomlevel))
            mid = [self._startPoint[0] + ddir[0]*dist/2, self._startPoint[1] + ddir[1]*dist/2]

            if self._startPoint[1] - self._endPoint[1] > 0:
                rotation = -angleBetween(getUnitVec([-1,0]), ddir)
            else:
                rotation = angleBetween(getUnitVec([-1,0]), ddir)

            rotation = (rotation-180)
            if self._startPoint[0] - self._endPoint[0] > 0 or dist == 0 :
                rotation = (rotation-180)
                mid = [mid[0]+norm[0]*taillength, mid[1]+norm[1]*taillength]
            else:
                mid = [mid[0]-norm[0]*taillength, mid[1]-norm[1]*taillength]

            self._canvas.create_text(mid[0], mid[1], anchor=CENTER, angle=rotation,font=font, text=sText1)


    def isInBounds(self, x, y):
        return False
