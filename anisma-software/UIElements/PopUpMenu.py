from tkinter import *
from render.RenderingObject import *

class PopUpMenu(RenderingObject):
    _title_height = 25
    _hoveredButton = -1

    def __init__(self, view, location, width, buttonHeight, title):
        self._parent = view.getCanvas()
        self._view = view
        self._location = location
        self._menuCanvas = Canvas(self._parent, width=width, height=100, bd=0, highlightthickness=0)
        self._width = width
        self._buttonHeight = buttonHeight
        self._title = title

        self._menuCanvas.bind("<Motion>", self.onMouseMoved)
        self._menuCanvas.bind("<ButtonPress-1>", self.onMousePressed)
        self._menuCanvas.bind("<Leave>", self.onMouseLeave)
        self._hidden = False
        self._buttons = []

    def isInBounds(self, x, y):
        return False

    def update(self, zoomlevel):
        if not self._hidden:
            title_height = self._title_height = 25

            font = ("Verdana", 12)
            bold_font = ("Verdana", 12, "bold")
            self._menuCanvas.create_rectangle(0, 0, self._width-1, title_height, fill='#EEEEEE', outline='#CCCCCC', width=1)
            self._menuCanvas.create_text(self._width/2.0-3.8*len(self._title), title_height/2.0, anchor=W, font=bold_font, text=self._title)

            for i in range(len(self._buttons)):
                buttonText = self._buttons[i].getTitle()
                if self._hoveredButton == i:
                    self._menuCanvas.create_rectangle(0, title_height + 1 + (self._buttonHeight) * (i), self._width-1, title_height + self._buttonHeight * (i+1), fill='#EEEEEE', outline='#EEEEEE', width=0.5)
                else:
                    self._menuCanvas.create_rectangle(0, title_height + 1 + (self._buttonHeight) * (i), self._width-1, title_height + self._buttonHeight * (i+1), fill='#DDDDDD', outline='#EEEEEE', width=0.5)
                self._menuCanvas.create_text(self._width / 2.0 - 3.2 * len(buttonText), title_height + self._buttonHeight * (i) + self._buttonHeight/2.0, anchor=W, font=font, text=buttonText)

            self._menuCanvas.place(x=self._location[0], y=self._location[1], height=title_height+len(self._buttons)*self._buttonHeight)

    def addButton(self, button):
        self._buttons.append(button)

    def getCanvas(self):
        return self._menuCanvas

    def onMouseMoved(self, event=None):
        if event.y > self._title_height and event.y < self._title_height + len(self._buttons)*self._buttonHeight:
            self._hoveredButton = int( (event.y - self._title_height) / self._buttonHeight )
        else:
            self._hoveredButton = -1
        self.update(0)

    def onMousePressed(self, event=None):
        if event.y > self._title_height and event.y < self._title_height + len(self._buttons)*self._buttonHeight:
            self._hoveredButton = int( (event.y - self._title_height) / self._buttonHeight )
            self._buttons[self._hoveredButton].onClick()
            self.remove()

    def onMouseReleased(self, event=None):
        return

    def onMouseLeave(self, event=None):
        self._hoveredButton = -1
        self.update(0)

    def hide(self):
        self._menuCanvas.place_forget()
        self._hidden = True

    def remove(self):
        self.hide()
        self._view.remove(self)

    def showAt(self, location):
        self._location = location
        self._hidden = False
        self.update(0)
