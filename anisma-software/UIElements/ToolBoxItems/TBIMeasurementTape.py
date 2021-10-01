from tkinter import *
from util.drawUtil import *
from UIElements.ToolBoxItem import ToolBoxItem
from ui.InteractionController import ToolMode, PencilType
from UIElements.IconButton import IconButton

class TBIMeasurementTape(IconButton):

    _nodecolor_fill_default = "#AAA"
    _nodecolor_fill = "#AAA"
    _nodecolor_fill_highlight = "#EEE"
    _nodecolor_outline = "#DDD"

    def __init__(self, canvas, iconpath, callback=None, ic=None):
        self._ic = ic
        super().__init__(canvas, 48, 48, iconpath, callback=callback, ic=ic)

    def setInfoCanvas(self, canvas, view=None):
        self._infoCanvas = canvas
        self._view = view

    def update(self):
        super().update()
        if self._view is not None:
            if self._activated:
                self._view.setTitle("Measuring Tape")
