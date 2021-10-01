from tkinter import *
from render.RenderingObject import *
from util.drawUtil import *

class AMTimeSlider(RenderingObject):

    def __init__(self, canvas, scene, view):
        self._canvas = canvas
        self._scene = scene
        self._view = view

    def isInBounds(self, x, y):
        size = [self._canvas.winfo_width(), self._canvas.winfo_height()]
        fraction = self._scene.getCurrentTime() / self._scene.getMaxTime()
        
        if x >= size[0]*fraction - 3 and x <= size[0]*fraction + 3:
            return True

        return False

    def update(self):
        color = "#12333D"

        if self.isHighlighted:
            color = "gray"

        size = [self._view.getTimeLineWidth()-self._view.getRightTimeInlet(), self._canvas.winfo_height()]
        fraction = self._scene.getCurrentTime() / self._scene.getMaxTime()

        trisize = 5
        width = 1
        self._canvas.create_line(self._view.getTimeLineInlet()+size[0]*fraction, self._view.getTopInlet(), self._view.getTimeLineInlet()+size[0]*fraction, size[1], width=width, joinstyle=ROUND, capstyle=ROUND, fill=color)
        self._canvas.create_polygon(self._view.getTimeLineInlet()+size[0]*fraction-trisize, self._view.getTopInlet()-trisize, self._view.getTimeLineInlet()+size[0]*fraction+trisize, self._view.getTopInlet()-trisize, self._view.getTimeLineInlet()+size[0]*fraction, trisize+self._view.getTopInlet()-trisize, fill=color, outline=color, width = 0)
