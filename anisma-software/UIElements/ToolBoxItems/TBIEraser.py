from tkinter import *
from util.drawUtil import *
from UIElements.ToolBoxItem import ToolBoxItem
from ui.InteractionController import ToolMode, PencilType
from UIElements.IconButton import IconButton

class TBIEraser(IconButton):

    _nodecolor_fill_default = "#AAA"
    _nodecolor_fill = "#AAA"
    _nodecolor_fill_highlight = "#EEE"
    _nodecolor_outline = "#DDD"

    def __init__(self, canvas, iconpath, callback=None, ic=None):
        self._ic = ic
        if callback is not None:
            super().__init__(canvas, 48, 48, iconpath, callback=callback, ic=ic)
        else:
            super().__init__(canvas, 48, 48, iconpath, callback=self._onBtnClick, ic=ic)
        self._l_shape = None
        self._dd_shapesval = None
        self._dd_shape = None

    def _onBtnClick(self, btn, ic):
        if self._ic.getToolMode() is ToolMode.ERASE_PRINTLAYER:
            self._ic.setToolMode(ToolMode.MANIPULATE)
        else:
            self._onSelect()

    def _onSelect(self, event=None):
        if self._dd_shapesval.get() == "rectangular":
            self._ic.setToolMode(ToolMode.ERASE_PRINTLAYER, pencilType=PencilType.RECTANGULAR)
        elif self._dd_shapesval.get() == "round":
            self._ic.setToolMode(ToolMode.ERASE_PRINTLAYER, pencilType=PencilType.ROUND)

    def setInfoCanvas(self, canvas, view=None):
        self._infoCanvas = canvas
        self._view = view

        # Shape
        self._l_shape = Label(self._infoCanvas, text = "Shape:",
        font=("Verdana", 18), background="#F4F7FA", foreground="#667587")

        options = ['rectangular','round']
        self._dd_shapesval = StringVar()
        self._dd_shapesval.set(options[0])
        self._dd_shape = OptionMenu(self._infoCanvas, self._dd_shapesval, *options, command=self._onSelect)
        self._dd_shape.config(width=20, font=("Verdana", 18), background="#F4F7FA", foreground="#12333D")

    def update(self):
        super().update()
        if self._l_shape is not None:
            if self._activated:
                padx = 24.5
                pady = 12
                self._view.setTitle("Erase Rigid Area")

                self._l_shape.grid(column = 0, row = 0, padx = padx, pady = pady, sticky=NW)
                self._dd_shape.grid(column = 0, row = 1, padx = padx, pady = 0, sticky=NW)
            else:
                self._l_shape.grid_forget()
                self._dd_shape.grid_forget()
