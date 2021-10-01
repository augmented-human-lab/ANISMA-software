from tkinter import *
from render.UIView import UIView
from UIElements.RadioButtonGroup import RadioButtonGroup
from UIElements.ToolBoxItems.TBISMAModule import TBISMAModule
from components.SMAWireParameters import SMAWireParameters

class UIToolBoxView(UIView):
    _font = ("Verdana", 16)

    def __init__(self, canvas, location):
        super().__init__(canvas)

        self._location = location
        self._show = True
        self._canvas = canvas
        self._listitems = []
        self._infoBoxObj = None
        self._radioItems = RadioButtonGroup()
        self._title = ""


        self._supporCanvasBar = Canvas(self._canvas.master, width=320, bd=0, highlightthickness=0, background="#F4F7FA")
        self._supporCanvasBar.pack_propagate(0)
        self._supporCanvasBar.pack(side=RIGHT, fill=Y, expand=0)

        self._topCan = Canvas(self._supporCanvasBar, width=320, height=81, bd=0, highlightthickness=0, background="#F4F7FA")
        self._topCan.pack(side=TOP)

        self._infoCanvas = Canvas(self._supporCanvasBar, width=320, bd=0, highlightthickness=0, background="#F4F7FA")
        self._infoCanvas.pack(side=TOP, fill=BOTH, expand=0)

        self._infoTextCan = Canvas(self._supporCanvasBar, width=320, bd=0, highlightthickness=0, background="#F4F7FA")
        self._infoTextCan.pack_propagate(0)
        self._infoTextCan.pack(side=TOP, fill=Y, expand=1)

        self.show(True)


    def show(self, enabled):
        self._show = enabled

        if enabled:
            self._canvas.place(x=self._location[0], y=self._location[1])
            self._canvas.config(background="#FFFFFF")
            self._supporCanvasBar.pack_propagate(0)
            self._supporCanvasBar.pack(side=RIGHT, fill=Y, expand=0)
        else:
            self._canvas.place_forget()
            self._supporCanvasBar.pack_forget()

    def addListItem(self, item):
        size = [int(self._canvas['width']), int(self._canvas['height'])]
        itemheight = 48
        itemwidth = 48
        itemstartY = 8+24 + len(self._listitems) * (itemheight+15)
        item.setLocation(size[0]/2, itemstartY)

        if len(self._listitems) == 1:
            item.setLocation(size[0]/2, itemstartY-10)
        if len(self._listitems) == 3:
            item.setLocation(size[0]/2, itemstartY-10)

        item.setSize(itemwidth, itemheight)
        item.setInfoCanvas(self._infoCanvas, view=self)

        self._listitems.append(item)
        self.add(item)
        item.setRadioGroup(self._radioItems)

        self.updateView()

    def setActiveListItem(self, item):
        self._radioItems.setActive(button=item)
        if item is None:
            self.setTitle("Nothing Selected")
        self.updateView()

    def getActiveListItem(self):
        return self._radioItems.getActiveButton()

    def setInfoBoxObj(self, obj):
        self._infoBoxObj = obj
        self.updateView()

    def setTitle(self, title):
        self._title = title

    def updateView(self):
        if self._show:
            self._canvas.delete("all")

            self._canvas.create_rectangle(1,1,self._canvas.winfo_width()-1, self._canvas.winfo_height()-1,fill="#FFFFFF", outline="#B0BAC5", width=1)
            self._canvas.create_line(self._canvas.winfo_width()*0.2, self._canvas.winfo_height()*2/5-10, self._canvas.winfo_width()*0.8, self._canvas.winfo_height()*2/5-10, fill="#B0BAC5", width = 1)
            self._canvas.create_line(self._canvas.winfo_width()*0.2, self._canvas.winfo_height()*4/5-10, self._canvas.winfo_width()*0.8, self._canvas.winfo_height()*4/5-10, fill="#B0BAC5", width = 1)
            for o in self._objects:
                o.update()


            self._topCan.delete("all")
            self._infoCanvas.delete("all")
            self._infoTextCan.delete("all")
            self._topCan.create_text(23, 35, anchor=NW, font=("Verdana", 20, "bold"), text=self._title, fill="#12333D")
            self._topCan.create_line(0, 80, 320, 80, fill="#B0BAC5", width = 1)

            self._supporCanvasBar.create_line(1, 0, 1, self._supporCanvasBar.winfo_height(), fill="#8091A5", width = 1)
            self._topCan.create_line(1, 0, 1, self._topCan.winfo_height(), fill="#8091A5", width = 1)
            self._infoCanvas.create_line(1, 0, 1, self._infoCanvas.winfo_height(), fill="#8091A5", width = 1)
            self._infoTextCan.create_line(1, 0, 1, self._infoTextCan.winfo_height(), fill="#8091A5", width = 1)

            size = [self._infoTextCan.winfo_width(), self._infoTextCan.winfo_height()]

            # # info box
            info_inlet = 220
            self._infoTextCan.create_line(0, 31.5, 320, 31.5, fill="#B0BAC5", width = 1)

            active = self.getActiveListItem()
            infotext = ""
            if active is not None:
                if isinstance(active, TBISMAModule):
                    infotext = active.getSMAParameters().getInfo()
            elif self._infoBoxObj is not None:
                if isinstance(self._infoBoxObj, SMAWireParameters):
                    infotext = self._infoBoxObj.getInfo()

            if infotext != "":
                self._infoTextCan.create_text(24, 49, anchor=NW, font=("Verdana", 14, "bold"), text="SMA SPECIFICATIONS:", fill="#667587")
                self._infoTextCan.create_text(24+15, 49+28+10, anchor=NW, font=("Verdana", 14, "normal"), text=infotext, fill="#667587")
