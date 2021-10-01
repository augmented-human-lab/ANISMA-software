from tkinter import *
from render.UIView import UIView
from UIElements.RadioButtonGroup import RadioButtonGroup
from UIElements.ToolBoxItems.TBISMAModule import TBISMAModule
from components.SMAWireParameters import SMAWireParameters

class UIIconToolBoxView(UIView):
    _font = ("Verdana", 16)

    def __init__(self, canvas, location, size):
        super().__init__(canvas)

        self._show = True
        self._canvas = canvas
        self._listitems = []
        self._infoBoxObj = None
        self._radioItems = RadioButtonGroup()

        canvas.config(background="#FFFFFF")
        self._infoCanvas = Canvas(self._canvas, width=(int(self._canvas['width'])-2), height=100, bd=0, highlightthickness=0, background="#FFFFFF")
        self.show(True)

    def show(self, enabled):
        self._show = enabled

        if enabled:
            self._canvas.place(x=location[0], y=location[1])
        else:
            self._canvas.pack_forget()

    def addListItem(self, item):
        size = [int(self._canvas['width']), int(self._canvas['height'])]

        itemheight = 60
        itemwidth = 48
        itemstartY = 80 + len(self._listitems) * itemheight

        item.setLocation(size[0]/2, itemstartY)
        item.setSize(itemwidth, itemheight)
        item.setInfoCanvas(self._infoCanvas)

        self._listitems.append(item)
        self.add(item)
        item.setRadioGroup(self._radioItems)

        self.updateView()

    def setActiveListItem(self, item):
        self._radioItems.setActive(button=item)
        self.updateView()

    def getActiveListItem(self):
        return self._radioItems.getActiveButton()

    def setInfoBoxObj(self, obj):
        self._infoBoxObj = obj
        self.updateView()

    def updateView(self):
        if self._show:
            super().updateView()
            size = [self._canvas.winfo_width(), self._canvas.winfo_height()]

            # draw seperator line
            self._canvas.create_line(size[0]-1, 0, size[0]-1, size[1], width=1, fill="black")
            self._canvas.create_text(size[0] / 2.0, 10, anchor=CENTER, font=("Verdana", 13, "bold"), text="Tool Box")

            # info box
            info_inlet = 220
            self._canvas.create_line(0, size[1]-info_inlet, size[0], size[1]-info_inlet, width=1, fill="black")
            self._canvas.create_text(10, size[1]-info_inlet+10, anchor=NW, font=("Verdana", 13, "bold"), text="Info:")

            active = self.getActiveListItem()
            infotext = ""
            if active is not None:
                if isinstance(active, TBISMAModule):
                    infotext = active.getSMAParameters().getInfo()
            elif self._infoBoxObj is not None:
                if isinstance(self._infoBoxObj, SMAWireParameters):
                    infotext = self._infoBoxObj.getInfo()
            self._canvas.create_text(10, size[1]-info_inlet+10+30, anchor=NW, font=("Verdana", 13), text=infotext)

            # draw seperator line
            self._canvas.create_line(0, size[1]-info_inlet*1.5-2, size[0], size[1]-info_inlet*1.5-2, width=1, fill="black")

            # Place info canvas
            self._infoCanvas.place(x=1.0, y=size[1]-info_inlet*1.5)
