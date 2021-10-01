from tkinter import *
from render.RenderingObject import *

class Grid(RenderingObject):

    __gridPadding = 10
    __origin = [0, 0]

    def __init__(self, canvas, width, height, printArea=None):
        self.__canvas = canvas
        self.__width = width
        self.__height = height
        self.__printArea = printArea
        self.__printerName = "Prusa i3 Mk3"

    def getPadding(self):
        return self.__gridPadding

    def update(self, zoomlevel):
        width = self.__width
        height = self.__height
        x_count = width / self.__gridPadding
        y_count = height / self.__gridPadding

        # Set shaded background and printing area background
        line = self.__canvas.create_rectangle(-width/2, -height/2, width/2, height/2, width=0, fill="#F3F5F9", outline="", tags="background")
        line = self.__canvas.create_rectangle(-self.__printArea[0]/2, -self.__printArea[1]/2, self.__printArea[0]/2, self.__printArea[1]/2, width=2, fill="#FFFFFF", outline="", tags="background")

        # Draw grid
        for i in range(0, width+1, self.__gridPadding):
            if i % 50 == 0:
                line = self.__canvas.create_line(i-width/2, 0-height/2, i-width/2, height-height/2, width=1, joinstyle=ROUND, capstyle=ROUND, fill="#AFB0B5", tags="level-5")
                self.__canvas.lower(line)
            else:
                line = self.__canvas.create_line(i-width/2, 0-height/2, i-width/2, height-height/2, width=1, joinstyle=ROUND, capstyle=ROUND, fill="#D9DCE2", tags="level-5")
                self.__canvas.lower(line)

        for i in range(0, height+1, self.__gridPadding):
            if i % 50 == 0:
                line = self.__canvas.create_line(0-width/2, i-height/2, width-width/2, i-height/2, width=1, joinstyle=ROUND, capstyle=ROUND, fill="#AFB0B5", tags="level-5")
                self.__canvas.lower(line)
            else:
                line = self.__canvas.create_line(0-width/2, i-height/2, width-width/2, i-height/2, width=1, joinstyle=ROUND, capstyle=ROUND, fill="#D9DCE2", tags="level-5")
                self.__canvas.lower(line)

        # Outline printing area
        line = self.__canvas.create_rectangle(-self.__printArea[0]/2, -self.__printArea[1]/2, self.__printArea[0]/2, self.__printArea[1]/2, width=1, fill="", outline="#B0BAC5", tags="level-5")
        self.__canvas.create_text(-self.__printArea[0]/2, -self.__printArea[1]/2 - 12/4, anchor=W, font=("Open Sans Light 300", int(5*zoomlevel)), fill="#8091A5", text="Print area - "+self.__printerName +" ("+ str(self.__printArea[0])+"x"+str(self.__printArea[1])+"mm)")

    def isInBounds(self, x, y):
        return False
