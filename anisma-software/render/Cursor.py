from tkinter import *
from render.RenderingObject import *
from components.SMASpringParameters import SMASpringParameters
from components.SMANode import SMANode
from util.drawUtil import *
from ui.InteractionController import PencilType

class Cursor(RenderingObject):

    __displayModule = False
    __location = [0,0]
    __size = 5
    __id = 0
    __infoText = ""
    __drawConnection = False

    __displayNode = False
    __connectionWidth = 6
    __locA = [0, 0]
    __springparams = None

    _module_rotation = 0
    _springcolor = "#12333D"
    _springcolor_highlighted = "#DDD"

    _nodecolor_fill_default = "#9473FF"
    _nodecolor_fill = "#9473FF"
    _nodecolor_fill_highlight = "#8038EB"
    _nodecolor_outline = "#3F4A56"
    _nodePosA = [0,0]
    _nodePosB = [0,0]
    _attachNodeA = None
    _attachNodeB = None

    __drawPrintLayerPencil = False
    __pencilSize = 7.5
    __pencilColor = "#8888CC"
    __pencilType = PencilType.RECTANGULAR

    def __init__(self, canvas, view):
        self.__canvas = canvas
        self.__view = view
        self._precontractlength = 0

        self._color_fill_loose = "#B0BAC5"
        self._color_outline_loose = "#12333D"
        self._color_outline_loose_highlight = "#CCC"
        self._color_fill_loose_highlight = "#AAA"

        self._color_fill_default = "#9473FF"
        self._color_fill = "#9473FF"
        self._color_fill_highlight = "#8038EB"
        self._color_outline = "#12333D"
        self._color_outline_highlight = "#9473FF"

    def setPreContractLength(self, val):
        self._precontractlength = val

    def getPreContractLength(self):
        return self._precontractlength

    def setSpringParams(self, params):
        self.__springparams = params

    def getLocation(self):
        return self.__location

    def setLocation(self, x, y):
        self.__location = [x, y]
        self.requestUpdate(self.__id)

    def __drawModule(self, zoomlevel, color='black'):

        length = self.getPreContractLength()
        dirVec = rotatePoint(1, 0, self._module_rotation)

        self._nodePosA = [self.__location[0] - dirVec[0] * length/2, self.__location[1] - dirVec[1] * length/2]
        self._nodePosB = [self.__location[0] + dirVec[0] * length/2, self.__location[1] + dirVec[1] * length/2]

        # check close nodes
        # reset if previously highlighted
        if self._attachNodeA is not None:
            self._attachNodeA.isHighlighted = False
        if self._attachNodeB is not None:
            self._attachNodeB.isHighlighted = False

        # check if attachable nodes are close
        self._attachNodeA = self.__view.findClosest(self._nodePosA, ofType=SMANode)
        self._attachNodeB = self.__view.findClosest(self._nodePosB, ofType=SMANode)

        # highlight attachable nodes and attach to close
        if self._attachNodeA is not None:
            self._attachNodeA.isHighlighted = True
            self._nodePosA = self._attachNodeA.getLocation()
            self._nodePosB = [self._nodePosA[0] + dirVec[0] * length, self._nodePosA[1] + dirVec[1] * length]
        if self._attachNodeB is not None:
            self._attachNodeB.isHighlighted = True
            self._nodePosB = self._attachNodeB.getLocation()
            self._nodePosA = [self._nodePosB[0] - dirVec[0] * length, self._nodePosB[1] - dirVec[1] * length]

        nodesize = 5
        color="#3F4A56"
        drawConnectionWithParams(self.__canvas, self._nodePosA, self._nodePosB, self.__springparams, zoomlevel, color=color)
        roundPolygon(self.__canvas, [self._nodePosA[0]-nodesize, self._nodePosA[0]-nodesize, self._nodePosA[0]+nodesize, self._nodePosA[0]+nodesize], [self._nodePosA[1]-nodesize, self._nodePosA[1]+nodesize, self._nodePosA[1]+nodesize, self._nodePosA[1]-nodesize], 2, width=1*zoomlevel, outline=self._nodecolor_outline, fill=self._nodecolor_fill)
        roundPolygon(self.__canvas, [self._nodePosB[0]-nodesize, self._nodePosB[0]-nodesize, self._nodePosB[0]+nodesize, self._nodePosB[0]+nodesize], [self._nodePosB[1]-nodesize, self._nodePosB[1]+nodesize, self._nodePosB[1]+nodesize, self._nodePosB[1]-nodesize], 2, width=1*zoomlevel, outline=self._nodecolor_outline, fill=self._nodecolor_fill)


    def update(self, zoomlevel):
        self.__cursorInfoTextID = self.__canvas.create_text(self.__location[0], self.__location[1] - 8, anchor=W, font="Verdana", text=self.__infoText)
        self.__canvas.tag_raise(self.__cursorInfoTextID)
        if self.__drawConnection:
            self.__id = self.__canvas.create_line(self.__locA[0], self.__locA[1], self.__location[0], self.__location[1], fill="#DDD", width=self.__connectionWidth*zoomlevel, joinstyle=ROUND, capstyle=ROUND)

        if self.__displayNode:
            roundPolygon(self.__canvas, [self.__location[0]-self.__size, self.__location[0]-self.__size, self.__location[0]+self.__size, self.__location[0]+self.__size], [self.__location[1]-self.__size, self.__location[1]+self.__size, self.__location[1]+self.__size, self.__location[1]-self.__size], 2, width=1*zoomlevel, fill="#EEE", outline="#DDD",)

        if self.__displayModule:
            self.__drawModule(zoomlevel, color=self._springcolor)\

        if self.__drawPrintLayerPencil:
            if self.__pencilType == PencilType.RECTANGULAR:
                self.__canvas.create_rectangle(self.__location[0]-self.__pencilSize, self.__location[1]-self.__pencilSize, self.__location[0]+self.__pencilSize, self.__location[1]+self.__pencilSize, fill=self.__pencilColor, outline="#888888", width=1)
            else:
                self.__canvas.create_oval(self.__location[0]-self.__pencilSize, self.__location[1]-self.__pencilSize, self.__location[0]+self.__pencilSize, self.__location[1]+self.__pencilSize, fill=self.__pencilColor, outline="#888888", width=1)


    def getAttachableNodeA(self):
        return self._attachNodeA

    def getAttachableNodeB(self):
        return self._attachNodeB

    def isInBounds(self, x, y):
        return False

    def setInfoText(self, text):
        self.__infoText = text

    def displayNode(self, enabled):
        self.__displayNode = enabled
        self.__displayModule = False
        self.__drawPrintLayerPencil = False

    def displayModule(self, enabled):
        self.__displayModule = enabled
        self.__displayNode = False
        self.__drawPrintLayerPencil = False
        self._module_rotation = 0
        self.setInfoText('')

    def getSMAModuleStartPos(self):
        return self._nodePosA

    def getSMAModuleEndPos(self):
        return self._nodePosB

    def rotateModule(self, angle):
        self._module_rotation += angle

        if self._module_rotation > 180:
            self._module_rotation -= 180
        elif self._module_rotation < 0:
            self._module_rotation += 180

        self.setInfoText(str(self._module_rotation) + '˚')

    def displayConnectionFrom(self, enabled, locationA=None):
        self.__drawConnection = enabled

        if locationA is not None:
            self.__locA = locationA
    def displayPrintLayerPencil(self, enabled):
        self.__drawPrintLayerPencil = enabled
        self.__displayModule = False
        self.__displayNode = False

    def setPencilType(self, pencilType):
        self.__pencilType = pencilType

    def setPencilSize(self, size):
        self.__pencilSize = size
