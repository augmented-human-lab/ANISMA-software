from tkinter import *
from tkinter.ttk import *
from util.drawUtil import *
from UIElements.IconButton import IconButton
from ui.InteractionController import ToolMode
from components.SMASpringParameters import SMASpringParameters

class TBISMAModule(IconButton):

    _nodecolor_fill_default = "#AAA"
    _nodecolor_fill = "#AAA"
    _nodecolor_fill_highlight = "#EEE"
    _nodecolor_outline = "#DDD"

    def __init__(self, canvas, iconpath, smaparams, ic=None):
        self._ic = ic
        self._smaparams = smaparams
        super().__init__(canvas, 48, 48, iconpath, callback=self._onBtnClick, ic=ic)

        self._dd_smatype = None
        self._l_smatype = None
        self._dd_smatypeval = None

        self._dd_smaprestretch = None
        self._l_smaprestretch = None
        self._dd_smaprestretchval = None

    def _onBtnClick(self, btn, ic):
        if self._ic.getToolMode() is ToolMode.PLACE_MODULE:
            self._ic.setToolMode(ToolMode.MANIPULATE)
        else:
            self._onSelect()

    def _onSelect(self, event=None):
        wireDiameter_mm = 0
        wireResistancePerMeter = 0
        springDiameter_mm = 0
        coilnumber = 0
        if self._dd_smatypeval.get() == "FLEXINOL: small, long":
            wireDiameter_mm = 0.203
            wireResistancePerMeter = 29.13
            springDiameter_mm = 1.37
            coilnumber = 30
        elif self._dd_smatypeval.get() == "FLEXINOL: small, short":
            wireDiameter_mm = 0.203
            wireResistancePerMeter = 29.13
            springDiameter_mm = 1.37
            coilnumber = 15
        elif self._dd_smatypeval.get() == "FLEXINOL: big, long":
            wireDiameter_mm = 0.381
            wireResistancePerMeter = 8.27
            springDiameter_mm = 2.54
            coilnumber = 16
        elif self._dd_smatypeval.get() == "FLEXINOL: big, short":
            wireDiameter_mm = 0.381
            wireResistancePerMeter = 8.27
            springDiameter_mm = 2.54
            coilnumber = 8
        self._smaparams = SMASpringParameters(wireDiameter_mm, wireResistancePerMeter, springDiameter_mm, 3.5, 6.5, coilnumber)

        # Set to the selected prestretch
        prestretch = self._dd_smaprestretchval.get()

        if prestretch == "0%":
            self._ic.setToolMode(ToolMode.PLACE_MODULE, smaparams=self._smaparams, smacontraction=0.0)
        elif prestretch == "50%":
            self._ic.setToolMode(ToolMode.PLACE_MODULE, smaparams=self._smaparams, smacontraction=0.5)
        elif prestretch == "100%":
            self._ic.setToolMode(ToolMode.PLACE_MODULE, smaparams=self._smaparams, smacontraction=1.0)

    def setInfoCanvas(self, canvas, view=None):
        self._infoCanvas = canvas
        self._view = view

        # SMA TYPE
        self._l_smatype = Label(self._infoCanvas, text = "Type:",
        font=("Verdana", 18), background="#F4F7FA", foreground="#667587")

        options = ['FLEXINOL: small, long','FLEXINOL: small, short','FLEXINOL: big, long', 'FLEXINOL: big, short',]
        self._dd_smatypeval = StringVar()
        self._dd_smatypeval.set(options[0])
        self._dd_smatype = OptionMenu(self._infoCanvas, self._dd_smatypeval, *options, command=self._onSelect)
        self._dd_smatype.config(width=20, font=("Verdana", 18), background="#F4F7FA", foreground="#12333D")


        # PRESTRETCH
        self._l_smaprestretch = Label(self._infoCanvas, text = "Initial Contraction Length:",
        font=("Verdana", 18), background="#F4F7FA", foreground="#667587")

        options = ['0%','50%','100%']
        self._dd_smaprestretchval = StringVar()
        self._dd_smaprestretchval.set(options[0])
        self._dd_smaprestretch = OptionMenu(self._infoCanvas, self._dd_smaprestretchval, *options, command=self._onSelect)
        self._dd_smaprestretch.config(width=20, font=("Verdana", 18), background="#F4F7FA", foreground="#12333D")

    def getSMAParameters(self):
        return self._smaparams

    def update(self):
        super().update()
        if self._l_smatype is not None:
            if self._activated:
                self._view.setTitle("SMA Module")
                padx = 24.5
                pady = 12
                self._l_smatype.grid(column = 0, row = 0, padx = padx, pady = pady, sticky=NW)
                self._dd_smatype.grid(column = 0, row = 1, padx = padx, pady = 0, sticky=NW)
                self._l_smaprestretch.grid(column = 0, row = 2, padx = padx, pady = pady, sticky=NW)
                self._dd_smaprestretch.grid(column = 0, row = 3, padx = padx, pady = 0, sticky=NW)
            else:
                self._l_smatype.grid_forget()
                self._dd_smatype.grid_forget()
                self._l_smaprestretch.grid_forget()
                self._dd_smaprestretch.grid_forget()
