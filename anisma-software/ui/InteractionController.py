from tkinter import *
from components.NodeFactory import *
from components.ConnectionFactory import *
from components.Node import Node
from enum import Enum
from UIElements.Button import Button
from UIElements.NodePopUpFactory import *
from components.SMANodeType import SMANodeType
from components.SMANode import SMANode
from components.SkinNode import SkinNode
from components.SkinSpring import SkinSpring
from animation.AMFactory import *
from components.MeasurementTape import MeasurementTape
from util.util import *
import copy
import sys

class ToolMode(Enum):
    MANIPULATE = 1
    PLACE_NODES = 2
    ADD_CONNECTION = 3
    PLACE_MODULE = 4
    DRAW_PRINTLAYER = 5
    ERASE_PRINTLAYER = 6
    MEASUREMENT_TAPE = 7

class PencilType(Enum):
    RECTANGULAR = 1
    ROUND = 2

class Mode(Enum):
    DESIGN = 1
    ANIMATE = 2
    FABRICATE = 3

class InteractionController():
    __mousePoint = [0.0, 0.0]
    __nodePointer = 0
    __view = None
    __grid = None
    __hoveredObject = None
    __mode = Mode.DESIGN
    __toolmode = ToolMode.PLACE_NODES
    __dragging = False
    __ui = None
    __toolmodeListeners = []
    __pencilType = []

    # add connection
    __startNode = None

    def __init__(self, window, canvas, view, ui, toolboxview, animationView, cursor, radioMode, scene, printLayer, grid=None):
        self.__window = window
        self.__canvas = canvas
        self.__cursor = cursor
        self.__view = view
        self.__animationView = animationView
        self.__ui = ui
        self.__toolboxview = toolboxview
        self._radioMode = radioMode
        self._scene = scene
        self._printLayer = printLayer

        self._tape = MeasurementTape(canvas, [0,0], [15,10])
        self._tape.show(False)
        view.add(self._tape)

        if sys.platform.startswith('darwin'):
            self.__canvas.bind("<ButtonPress-2>", self.onMousePressedOnViewRight)
        else:
            self.__canvas.bind("<ButtonPress-3>", self.onMousePressedOnViewRight)

        self.__canvas.bind("<ButtonPress-1>", self.onMousePressedOnView)
        self.__canvas.bind("<ButtonRelease-1>", self.onMouseReleasedOnView)
        self.__ui.getCanvas().bind("<ButtonPress-1>", self.onMousePressedOnUI)
        self.__ui.getCanvas().bind("<ButtonRelease-1>", self.onMouseReleasedOnUI)

        self.__canvas.bind("<Motion>", self.onMouseMovedOnView)
        self.__canvas.bind("<B1-Motion>", self.onMouseMovedOnView)
        self.__ui.getCanvas().bind("<Motion>", self.onMouseMovedOnUI)
        self.__window.bind("<KeyPress-Alt_L>", self.onBtnControlPress)
        self.__window.bind("<KeyRelease-Alt_L>", self.onBtnControlRelease)
        self.__window.bind("<MouseWheel>", self.on_scroll)
        self.__window.bind("<KeyPress-Escape>", self.onBtnEscapePress)

        self.__canvas.bind("<Enter>", self.onMouseEnter)
        self.__canvas.bind("<Leave>", self.onMouseLeave)

        if grid is not None:
            self.__grid = grid

        self.__mousePressedOnView = False
        self.__createdPopUp = None
        self.__springparams = None

        self._startDraggingNodesPos = [[0,0], [0,0]]
        self._startDraggingPos = [0, 0]
        self.__pencilSize = 7.5
        self.__pencilThickness = 3
        self.__cursor.setPencilSize(self.__pencilSize)

        self._attachableNode = None
        self.__arrangement_changed = False
        self._ignoreNodeWeight = False

    def on_scroll(self, event):
        if self.__toolmode == ToolMode.PLACE_MODULE:
            self.__cursor.rotateModule(event.delta*15)
            self.__view.updateView()

        if self.__toolmode == ToolMode.DRAW_PRINTLAYER or self.__toolmode == ToolMode.ERASE_PRINTLAYER:
            self.__pencilSize += event.delta

            self.__pencilSize = min(100, max(5, self.__pencilSize))

            self.__cursor.setPencilSize(self.__pencilSize)

        self.__view.updateView()

    def onBtnEscapePress(self, event):
        self.setToolMode(ToolMode.MANIPULATE)

    def updateNode(self, node):
        # I wanted to update sth but forgot what. Maybe not even necessary anymore 
        # self._scene.updateNode(node)
        return

    def onMouseMovedOnUI(self, event=None):
        self.__mousePoint = [event.x,event.y]

        # find closest component
        obj = self.__ui.findClosest(self.__mousePoint)

        # if found one highlight it
        if obj is None:
            self.__window.config(cursor="")

        self.setHoveredObject(obj)

        self.__ui.updateView()
        self.__view.updateView()

    def _drawOnPrintLayer(self, erease=False):
        if self.__pencilType == PencilType.RECTANGULAR:
            self._printLayer.addRectangularPrintArea(self.__cursor.getLocation(), size=self.__pencilSize, erease=erease, thickness=self.__pencilThickness)
        else:
            self._printLayer.addCircularPrintArea(self.__cursor.getLocation(), size=self.__pencilSize, erease=erease, thickness=self.__pencilThickness)

    def getGridAlignedPos(self, coords):
        if self.__grid is not None and self.__view.isGridActivated() and not (isinstance(self.__hoveredObject, SMANode) and self.__hoveredObject.getType() == SMANodeType.LOOSE):
            padding = self.__grid.getPadding()
            coords[0] = int((coords[0] + (padding if coords[0] >= 0 else -padding)/2.0) / padding) * padding
            coords[1] = int((coords[1] + (padding if coords[1] >= 0 else -padding)/2.0) / padding) * padding
        return coords

    def onMouseMovedOnView(self, event=None):
        self.__mousePoint = [event.x,event.y]
        zoom = self.__view.getZoom()
        coords = [(self.__canvas.canvasx(0) + event.x) / zoom, (self.__canvas.canvasy(0) + event.y) / zoom]
        rawCoords = [coords[0], coords[1]]

        # Apply grid constraint to cursor pos
        if self.__grid is not None and self.__view.isGridActivated() and not (isinstance(self.__hoveredObject, SMANode) and self.__hoveredObject.getType() == SMANodeType.LOOSE):
            padding = self.__grid.getPadding()
            coords[0] = int((coords[0] + (padding if coords[0] >= 0 else -padding)/2.0) / padding) * padding
            coords[1] = int((coords[1] + (padding if coords[1] >= 0 else -padding)/2.0) / padding) * padding

        self.__cursor.setLocation(coords[0], coords[1])

        if self.__dragging:
            if self.__hoveredObject is not None:
                if self.__mode != Mode.ANIMATE or isinstance(self.__hoveredObject, SMANode) and self.__hoveredObject.getType() == SMANodeType.LOOSE:
                    if self.__toolmode is not ToolMode.ADD_CONNECTION and isinstance(self.__hoveredObject, SMANode): # dragging node and highlight attachable nodes
                        # unhighlight any prior attachable node
                        if self._attachableNode is not None:
                            self._attachableNode.isHighlighted = False

                        self._attachableNode = self.__view.findClosest(self.__hoveredObject.getLocation(), ofType=SMANode, excluding=self.__hoveredObject)
                        if self._attachableNode is not None:
                            self._attachableNode.isHighlighted = True

                        self.__hoveredObject.setLocation(coords[0], coords[1])
                        self.setMadeChange()
                        self.updateNode(self.__hoveredObject)
                    elif isinstance(self.__hoveredObject, SMAConnection): # dragging connection
                        nodes = self.__hoveredObject.getNodes()

                        if self.__grid is not None and self.__view.isGridActivated() and not (isinstance(self.__hoveredObject, SMANode) and self.__hoveredObject.getType() == SMANodeType.LOOSE):
                            padding = self.__grid.getPadding()
                            self._startDraggingPos[0] = int((self._startDraggingPos[0] + (padding if self._startDraggingPos[0] >= 0 else -padding)/2.0) / padding) * padding
                            self._startDraggingPos[1] = int((self._startDraggingPos[1] + (padding if self._startDraggingPos[1] >= 0 else -padding)/2.0) / padding) * padding

                        displaced = [coords[0]-self._startDraggingPos[0], coords[1]-self._startDraggingPos[1]]

                        nodes[0].setLocation(self._startDraggingNodesPos[0][0]+displaced[0], self._startDraggingNodesPos[0][1]+displaced[1])
                        nodes[1].setLocation(self._startDraggingNodesPos[1][0]+displaced[0], self._startDraggingNodesPos[1][1]+displaced[1])
                        self.updateNode(nodes[0])
                        self.updateNode(nodes[1])
                        self.setMadeChange()
            if self.__toolmode == ToolMode.DRAW_PRINTLAYER:
                self._drawOnPrintLayer()
            elif self.__toolmode == ToolMode.ERASE_PRINTLAYER:
                self._drawOnPrintLayer(erease=True)
            elif self.__toolmode == ToolMode.MEASUREMENT_TAPE:
                self._tape.setEndLocation(coords)

            if isinstance(self.__hoveredObject, SkinNode):
                force = [coords[0]-self._startDraggingPos[0], coords[1]-self._startDraggingPos[1]]
                force = [10/1000, 10/1000]
                self.__hoveredObject.setDraggingForce(force)
            if isinstance(self.__hoveredObject, SkinSpring):
                force = [coords[0]-self._startDraggingPos[0], coords[1]-self._startDraggingPos[1]]
                nodes = self.__hoveredObject.getNodes()

                force = [10/1000, 10/1000]
                nodes[0].setDraggingForce(force)
                nodes[1].setDraggingForce(force)
        else:
            if self.__toolmode == ToolMode.MEASUREMENT_TAPE:
                self._tape.drawCursorAt(coords)

            ## Highlight hovered component
            # un highlight last
            if self.__hoveredObject is not None:

                if isinstance(self.__hoveredObject, SMANode):
                    self.__hoveredObject.displayBounds(False)

                if isinstance(self.__hoveredObject, SMAConnection):
                    self.__toolboxview.setInfoBoxObj(self.__hoveredObject.getSMAParameters())

                    if self.__hoveredObject.hasError():
                        self.__cursor.setInfoText(self.__hoveredObject.getLastError())
                    else:
                        self.__cursor.setInfoText("")
                else:
                    self.__toolboxview.setInfoBoxObj(None)
                    self.__cursor.setInfoText("")
            else:
                self.__toolboxview.setInfoBoxObj(None)
                self.__cursor.setInfoText("")


        if self.__hoveredObject is not None:

            if isinstance(self.__hoveredObject, SMANode):
                self.__hoveredObject.displayBounds(False)


        if not self.__dragging or self.__toolmode == ToolMode.ADD_CONNECTION:
            # find closest component
            obj = self.__view.findClosest(rawCoords)

            # if found one highlight it
            if self.__toolmode != ToolMode.DRAW_PRINTLAYER and self.__toolmode != ToolMode.ERASE_PRINTLAYER:
                if obj is not None:

                    if sys.platform.startswith('darwin'):
                        self.__window.config(cursor="hand")
                    else: 
                        self.__window.config(cursor="hand1")
                else:
                    self.__window.config(cursor="")

                if self.__toolmode is ToolMode.ADD_CONNECTION:
                    self.setHoveredObject(None)
                    if isinstance(obj, SMANode):
                        self.setHoveredObject(obj)
                else:
                    self.setHoveredObject(obj)
            else:
                self.setHoveredObject(None)

        if isinstance(self.__hoveredObject, SMANode):
            self.__hoveredObject.displayBounds(True)

        self.__view.updateView()
        self.__ui.updateView()

        if self.__mousePressedOnView:
            self.__view.do_pan(event)

    def setHoveredObject(self, newobj):
        if self.__hoveredObject is not None:
            self.__hoveredObject.isHighlighted = False

            # unhighlight linked track
            if isinstance(self.__hoveredObject, SMAConnection):
                track = self._scene.getTrackFor(self.__hoveredObject)
                if track is not None:
                    track.setHighlighted(False)
                    self.__animationView.updateView()

        self.__hoveredObject = newobj

        if self.__hoveredObject is not None:
            self.__hoveredObject.isHighlighted = True

            # highlight linked track
            if isinstance(self.__hoveredObject, SMAConnection):
                track = self._scene.getTrackFor(self.__hoveredObject)
                if track is not None:
                    track.setHighlighted(True)
                    self.__animationView.updateView()


    def onMousePressedAnywhere(self):
        if self.__createdPopUp is not None:
            self.__createdPopUp.remove()
            self.__createdPopUp = None


    def onMousePressedOnUI(self, event=None):
        if isinstance(self.__hoveredObject, Button):
            self.__hoveredObject.onClick()
        self.__ui.updateView()

        self.onMousePressedAnywhere()

    def onMouseReleasedOnUI(self, event=None):
        print("UI Mouse Release")

    def __setSpringParams(self, params):
        self.__springparams = params
        self.__cursor.setSpringParams(self.__springparams)

    def onMousePressedOnViewRight(self, event=None):
        if self.__createdPopUp is not None:
            self.__createdPopUp.remove()
            self.__createdPopUp = None

        if isinstance(self.__hoveredObject, SMANode):
            self.__createdPopUp = createNodePopUp(self.__hoveredObject, self.__view, [event.x, event.y])
        elif isinstance(self.__hoveredObject, SMAConnection):
            self.__createdPopUp = createConnectionPopUp(self.__hoveredObject, self.__view, [event.x, event.y])
        self.setToolMode(ToolMode.MANIPULATE)

        self.__window.config(cursor="")
        self.__view.updateView()

    def _openActuationBehaviorPopUp(self, event=None):
        if self.__createdPopUp is not None:
            self.__createdPopUp.remove()
            self.__createdPopUp = None

        self.__createdPopUp = createAMSMAPopUp(self.__hoveredObject, self.__view, [event.x, event.y], self._scene)
        self.setToolMode(ToolMode.MANIPULATE)
        self.__window.config(cursor="")
        self.__view.updateView()

    def onMousePressedOnView(self, event=None):
        self.__dragging = True
        zoom = self.__view.getZoom()
        self._startDraggingPos = [(self.__canvas.canvasx(0) + event.x) / zoom, (self.__canvas.canvasy(0) + event.y) / zoom]

        if self.__toolmode == ToolMode.MANIPULATE:
            if self.__hoveredObject is not None:
                self.__view.setPanning(False)

                if isinstance(self.__hoveredObject, SMANode) and self.__hoveredObject.getType() == SMANodeType.LOOSE:
                    self.__hoveredObject.setMovable(True)
                elif isinstance(self.__hoveredObject, SMAConnection):
                    nodes = self.__hoveredObject.getNodes()
                    self._startDraggingNodesPos = [nodes[0].getLocation(), nodes[1].getLocation()]
        elif self.__toolmode == ToolMode.DRAW_PRINTLAYER:
            self.__view.setPanning(False)
            self._drawOnPrintLayer()
        elif self.__toolmode == ToolMode.ERASE_PRINTLAYER:
            self.__view.setPanning(False)
            self._drawOnPrintLayer(erease=True)
        elif self.__toolmode == ToolMode.ADD_CONNECTION:
            if isinstance(self.__hoveredObject, SMANode):
                self.__startNode = self.__hoveredObject
            elif self.__hoveredObject is None:
                node = createSMANode(self.__view, self.__cursor.getLocation())
                self.setMadeChange()
                self.__startNode = node

            self.__view.setPanning(False)
            self.__cursor.displayConnectionFrom(True, locationA=self.__startNode.getLocation())

        elif self.__toolmode == ToolMode.MEASUREMENT_TAPE:
            pos = self.getGridAlignedPos(self._startDraggingPos)
            self._tape.setStartLocation(pos)
            self._tape.setEndLocation(pos)
            self._tape.show(True)
            self.__view.setPanning(False)

        self.__mousePressedOnView = True
        self.__view.do_prePan(event)

        if self.__mode == Mode.ANIMATE and isinstance(self.__hoveredObject, SMAConnection):
            self._openActuationBehaviorPopUp(event=event)
        else:
            self.onMousePressedAnywhere()

    def onMouseReleasedOnView(self, event=None):
        self.__dragging = False

        if isinstance(self.__hoveredObject, SkinNode):
            force = [0,0]
            self.__hoveredObject.setDraggingForce(force)
        if isinstance(self.__hoveredObject, SkinSpring):
            force = [0,0]
            nodes = self.__hoveredObject.getNodes()
            nodes[0].setDraggingForce(force)
            nodes[1].setDraggingForce(force)

        if self.__toolmode == ToolMode.PLACE_NODES and self.__hoveredObject is None: # placing a single node
            self.setMadeChange()
            nodeA = createSMANode(self.__view, self.__cursor.getLocation())
            self.__view.updateView()
        elif self.__toolmode == ToolMode.MANIPULATE:
            if isinstance(self.__hoveredObject, SMANode): # attaching a node

                if self._attachableNode is not None:
                    neighbours = self.__hoveredObject.getAllNeighbourNodes()
                    if self._attachableNode not in neighbours:
                        connectionExists = False

                        for n in neighbours:
                            if self.__view.connectionExists(n, self._attachableNode):
                                connectionExists = True

                        if not connectionExists:
                            self.__view.remove(self.__hoveredObject, recurse=False)
                            self.__hoveredObject.replaceWith(self._attachableNode)
                            self.setMadeChange()
                            self.checkSMAControlRequirements()

                if self.__hoveredObject.getType() == SMANodeType.LOOSE and self.__hoveredObject not in self._scene.getRecordedNodes():
                    self.__hoveredObject.setMovable(False)

                self.__view.updateView()
            elif isinstance(self.__hoveredObject, SMAConnection): # connecting an SMA to existing nodes
                nodes = self.__hoveredObject.getNodes()
                attachNodeA = self.__view.findClosest(nodes[0].getLocation(), ofType=SMANode, excluding=nodes[0])
                attachNodeB = self.__view.findClosest(nodes[1].getLocation(), ofType=SMANode, excluding=nodes[1])

                # if there exists no connection with attachNodeA and attachNOdeB
                if attachNodeA is not None and attachNodeB is not None:
                    if not self.__view.connectionExists(attachNodeA, attachNodeB):
                        self.__view.remove(nodes[0], recurse=False)
                        self.__view.remove(nodes[1], recurse=False)

                        nodes[0].replaceWith(attachNodeA)
                        nodes[1].replaceWith(attachNodeB)
                    self.setMadeChange()
                    self.checkSMAControlRequirements()

                elif attachNodeA is not None and attachNodeB is None:
                    self.__view.remove(nodes[0], recurse=False)
                    nodes[0].replaceWith(attachNodeA)
                    self.setMadeChange()
                    self.checkSMAControlRequirements()

                elif attachNodeA is None and attachNodeB is not None:
                    self.__view.remove(nodes[1], recurse=False)
                    nodes[1].replaceWith(attachNodeB)
                    self.setMadeChange()
                    self.checkSMAControlRequirements()

                self.__view.updateView()
        elif self.__toolmode == ToolMode.ADD_CONNECTION:
            # connect to existing or just created node
            if self.__startNode is not None:
                # add a node if no node is hovered
                if self.__hoveredObject is None:
                    nodeA = createSMANode(self.__view, self.__cursor.getLocation())
                    self.setHoveredObject(nodeA)
                    self.setMadeChange()

                self.__startNode.resetColor()
                self.__cursor.displayConnectionFrom(False)
                if isinstance(self.__hoveredObject, SMANode) and (self.__startNode is not self.__hoveredObject): # connect the end node of a new connection to an existing node
                    if not self.__view.connectionExists(self.__startNode, self.__hoveredObject):
                        length = getDistance(self.__startNode.getLocation(), self.__hoveredObject.getLocation())
                        length -= 10
                        createSMAConnection(self.__view, self.__startNode, self.__hoveredObject, params=copy.copy(self.__springparams), forLength=length, smacontraction=self._smacontraction)
                        self.setMadeChange()
                        self.checkSMAControlRequirements()
        elif self.__toolmode == ToolMode.PLACE_MODULE:  # create a new module and connect it to existing nodes that are close
            nodeA = self.__cursor.getAttachableNodeA()
            nodeB = self.__cursor.getAttachableNodeB()
            if nodeA is None:
                nodeA = createSMANode(self.__view, self.__cursor.getSMAModuleStartPos())
                self.setMadeChange()
                self.checkSMAControlRequirements()
            if nodeB is None:
                nodeB = createSMANode(self.__view, self.__cursor.getSMAModuleEndPos())
                self.setMadeChange()
                self.checkSMAControlRequirements()
            if not self.__view.connectionExists(nodeA, nodeB):
                createSMAConnection(self.__view, nodeA, nodeB, params=copy.copy(self.__springparams))
                self.setMadeChange()
                self.checkSMAControlRequirements()

            self.__view.updateView()

        self.__view.setPanning(True)
        self.__mousePressedOnView = False


    def onBtnControlPress(self, event=None):
        self.__view.setGridActivated(True)

    def onBtnControlRelease(self, event=None):
        self.__view.setGridActivated(False)

    def getToolMode(self):
        return self.__toolmode

    def setToolMode(self, mode, smaparams=None, pencilType=None, pl_thickness=None, smacontraction=-1):

        if smacontraction > -1:
            nodesize = 10
            self._smacontraction = smacontraction
            max = smaparams.getContractedLength()+nodesize
            min = smaparams.getExtendedLength()+nodesize
            contraction = min + (max - min)*(smacontraction)
            self.__cursor.setPreContractLength(contraction)

        self.__toolmode = mode

        self.__setSpringParams(smaparams)
        if pencilType is not None:
            self.__pencilType = pencilType
            self.__cursor.setPencilType(pencilType)

        if pl_thickness is not None:
            self.__pencilThickness = pl_thickness

        print("switching to ", self.__toolmode)

        if self.__toolmode == ToolMode.PLACE_NODES:
            self.__cursor.displayNode(True)
        elif self.__toolmode == ToolMode.ADD_CONNECTION:
            self.__cursor.displayNode(True)
        elif self.__toolmode == ToolMode.PLACE_MODULE:
            self.__view.setZooming(False)
            self.__cursor.displayModule(True)
        elif self.__toolmode == ToolMode.DRAW_PRINTLAYER or self.__toolmode == ToolMode.ERASE_PRINTLAYER:
            self.__cursor.displayPrintLayerPencil(True)
            self.__view.setZooming(False)
        else:
            if self.__toolmode == ToolMode.MANIPULATE:
                self.__toolboxview.setActiveListItem(None) # unselect any
            self.__view.setZooming(True)
            self.__cursor.displayPrintLayerPencil(False)
            self.__cursor.displayNode(False)

        self._tape.show(False)

        self.__ui.updateView()
        self.__view.updateView()
        self.__animationView.updateView()
        self.__toolboxview.updateView()

    def setMode(self, mode):
        self.__mode = mode

        if mode == Mode.DESIGN:
            self._radioMode.setActive(btnNum=0)
            self.__view.showGrid(True)
        elif mode == Mode.ANIMATE:
            self._radioMode.setActive(btnNum=1)
            self.__view.showGrid(False)
        elif mode == Mode.FABRICATE:
            self._radioMode.setActive(btnNum=2)

        self.__ui.updateView()
        self.__view.updateView()

    def addModeListener(self, listener):
        self.__toolmodeListeners.append(listener)

    def onMouseLeave(self, event=None):
        self.__window.config(cursor="")

    def onMouseEnter(self, event=None):
        return

    def setToUnchanged(self):
        self.__arrangement_changed = False

    def didMakeChanges(self):
        return self.__arrangement_changed

    def setMadeChange(self):
        self.__arrangement_changed = True
        self._scene.resetAnimationHasRun()

    def checkSMAControlRequirements(self):
        if not self._ignoreNodeWeight:
            foundExceedingWeight = False
            nodes = []

            # prepare export
            objs = self.__view.getAllObjects()
            for o in objs:
                if isinstance(o, SMANode):
                    nodes.append(o)

            for n in nodes:
                conns = n.getConnections()
                nodeWeight = 0

                for c in conns:
                    smaparams = c.getSMAParameters()

                    if smaparams.getSpringDiameter() == 1.37:
                        nodeWeight += 1
                    elif smaparams.getSpringDiameter() == 2.54:
                        nodeWeight += 2

                if nodeWeight > 4:
                    foundExceedingWeight = True

            if foundExceedingWeight:
                print("Warning: Too many SMAs added to Node that are not supported.")
                MsgBox = messagebox.askokcancel('Warning: Overloaded Node', 'With the current Controllerboard only 4 small or 2 big SMAs are supported for a single Node. It is recommended to delete any further SMAs.\n\n(By selecting cancel, this message will not pop up again.)', icon = 'warning')

                if not MsgBox:
                    self._ignoreNodeWeight = True
