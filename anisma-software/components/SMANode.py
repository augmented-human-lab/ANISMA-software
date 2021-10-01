from tkinter import *
from render.RenderingObject import *
from components.Node import Node
from components.SMANodeType import SMANodeType
from shapely.geometry import Point, MultiPoint, MultiPolygon, LineString
from util.util import *
from util.drawUtil import *
from util.globalvars import *
from controller.Controller import NodePolarity
from util.NodePhaseLogic import *

class SMANode(Node, NodePhaseLogic):

    _resetToEMA = True
    _displayBounds = False

    def __init__(self, canvas, type=SMANodeType.SOLID):
        super().__init__(canvas)
        self.setType(type)

        self._originLocation = [0, 0]
        self._newlocation = [0, 0]
        self._velocity = [0, 0]
        self._acceleration = [0, 0]
        self._mass = 1
        self._pin = 0
        self._polarity = NodePolarity.OFF
        self._skinNodes = []
        self._oldlocation = []
        self._initcenter = [0,0]
        self._EMA_color = "#dcf7e0" 

        self._displayPin = False

    def displayPin(self, enabled):
        self._displayPin = enabled

    def getPolarity(self):
        return self._polarity

    def setPolarity(self, polarity):
        self._polarity = polarity

    def getLocation(self):
        return self._location

    def setLocation(self, x, y):
        self._location = [x, y]
        self._canvas.coords(self._id, self._location[0]-self._size, self._location[1]-self._size, self._location[0]+self._size, self._location[1]+self._size)
        self.requestUpdate(self._id)

    def _drawEffectiveMovementArea(self, zoomlevel, reset):
        if len(self._connections) < 2:
            print("not movable")
        elif self._type == SMANodeType.LOOSE or (self.isHighlighted):
            intersectPoints = flattenPolyStruct(self.getEMAPoly(loose = (self._type == SMANodeType.LOOSE)))
            if len(intersectPoints) > 0:
                allPoints = []
                for p in intersectPoints:

                    # collect points
                    for i in range(len(p)):
                        if i % 2 == 0:
                            allPoints.append([p[i],p[i+1]])

                    # create EMA polygon
                    pid = self._canvas.create_polygon(p, fill=self._EMA_color, smooth=True, tags="level-4")
                    self._canvas.lower(pid)

                # set node to center
                if reset:
                    self._location = getCentroid(allPoints)

    def getEMAPoly(self, buffer=7.5, loose=False):
        if loose and len(self._connections) == 2:
            nodePosA = self._connections[0].getOtherNode(self).getLocation()
            nodePosB = self._connections[1].getOtherNode(self).getLocation()

            # get normalised vec
            vecA = [nodePosB[0] - nodePosA[0], nodePosB[1] - nodePosA[1]]
            magA = magnitude(vecA)
            vecA = [vecA[0] / magA, vecA[1] / magA]

            distanceAB = getDistance(nodePosA, nodePosB)
            minDist = self._connections[0].getMinLength()
            maxDist = self._connections[0].getMaxLength()
            movableDist = distanceAB - minDist * 2

            lineStart = [0,0]
            lineEnd = [0,0]

            if distanceAB > 2*maxDist or distanceAB < 2*minDist:
                # not movable at all
                print("not movable")
            elif distanceAB > maxDist+minDist:
                # then limited by max bounds
                movableDist = maxDist*2 - distanceAB
                minS = ( distanceAB - movableDist ) / 2
                lineStart = [nodePosA[0] + vecA[0] * minS, nodePosA[1] + vecA[1] * minS]
                lineEnd = [nodePosA[0] + vecA[0] * (minS + movableDist), nodePosA[1] + vecA[1] * (minS + movableDist)]
            else:
                lineStart = [nodePosA[0] + vecA[0] * minDist, nodePosA[1] + vecA[1] * minDist]
                lineEnd = [nodePosA[0] + vecA[0] * (minDist + movableDist), nodePosA[1] + vecA[1] * (minDist + movableDist)]

            return LineString([lineStart, lineEnd]).buffer(buffer)
        else:
            # collect circles from neighbor nodes
            circlesIn = []
            circlesOut = []
            connectedNodes = []

            for c in self._connections:
                for n in c._nodes:
                    if (n.getLocation()[0] != self.getLocation()[0]) or (n.getLocation()[1] != self.getLocation()[1]):
                        circlesOut.append(Circle((n.getLocation()[0], n.getLocation()[1]), c.getMaxLength()))
                        circlesIn.append(Circle((n.getLocation()[0], n.getLocation()[1]), c.getMinLength()))
                        connectedNodes.append(n.getLocation())

            return getIntersectionPolygon(circlesIn, circlesOut, connectedNodes, looseNode=(self._type == SMANodeType.LOOSE))

    def _adjustPosition(self):

        if len(self._connections) > 1:
            center = [0,0]

            if len(self._connections) > 2:  # depricated
                # get pos of all neighbor nodes
                nodepositions = []
                for c in self._connections:
                    n = c.getOtherNode(self)
                    nodepositions.append(n.getLocation())
            else:
                nodePosA = self._connections[0].getOtherNode(self).getLocation()
                nodePosB = self._connections[1].getOtherNode(self).getLocation()

                # get normalised vec
                vecA = [nodePosB[0] - nodePosA[0], nodePosB[1] - nodePosA[1]]
                magA = magnitude(vecA)
                vecA = [vecA[0] / magA, vecA[1] / magA]
                dist = getDistance(nodePosA, nodePosB) / 2

                center = [nodePosA[0] + (vecA[0]*dist), nodePosA[1] + (vecA[1]*dist)]

                if self._resetToEMA:
                    self._location = center


    def update(self, zoomlevel):
        if self._type == SMANodeType.LOOSE:
            self._adjustPosition()
            self._drawEffectiveMovementArea(zoomlevel, self._resetToEMA)
        else:
            # draw indicators for connection limits based on selectd node
            if self._displayBounds and self._type != SMANodeType.LOOSE:
                self._drawEffectiveMovementArea(zoomlevel, False)
                if len(self._connections) == 1:
                    max = self._connections[0].getMaxLength()
                    min = self._connections[0].getMinLength()
                    otherNode = self._connections[0].getOtherNode(self)
                    otherLoc = otherNode.getLocation()
                    med = min + (max - min) / 2

                    dID = self._canvas.create_oval(otherLoc[0]-med, otherLoc[1]-med, otherLoc[0]+med, otherLoc[1]+med, outline=self._color_outline, width=1, dash=(10, 10), tags="level-4")
                    dID = self._canvas.create_oval(otherLoc[0]-min, otherLoc[1]-min, otherLoc[0]+min, otherLoc[1]+min, outline=self._color_outline, width=0, fill="white", tags="level-3")
                    dID = self._canvas.create_oval(otherLoc[0]-max, otherLoc[1]-max, otherLoc[0]+max, otherLoc[1]+max, outline=self._color_outline, width=0, fill=self._EMA_color, tags="level-2")

        location = self._location

        if self.isHighlighted:
            if self._type == SMANodeType.SOLID:
                roundPolygon(self._canvas, [location[0]-self._size, location[0]-self._size, location[0]+self._size, location[0]+self._size], [location[1]-self._size, location[1]+self._size, location[1]+self._size, location[1]-self._size], 10, width=1.0*zoomlevel, outline=self._color_outline_highlight, fill=self._color_fill_highlight)
            elif self._type == SMANodeType.ELASTIC:
                dID = roundPolygon(self._canvas, [self.getLocation()[0]-self._size, self.getLocation()[0]-self._size, self.getLocation()[0]+self._size, self.getLocation()[0]+self._size], [self.getLocation()[1]-self._size, self.getLocation()[1]+self._size, self.getLocation()[1]+self._size, self.getLocation()[1]-self._size], 2, width=0, outline=self._color_outline_highlight, fill=self._color_fill_highlight)
                self._canvas.lower(dID)
                roundPolygon(self._canvas, [location[0]-self._size, location[0]-self._size, location[0]+self._size, location[0]+self._size], [location[1]-self._size, location[1]+self._size, location[1]+self._size, location[1]-self._size], 2, width=1.0*zoomlevel, outline=self._color_outline_highlight, fill=self._color_fill_highlight)
            else:
                self._id = self._canvas.create_oval(location[0]-self._size, location[1]-self._size, location[0]+self._size, location[1]+self._size, fill=self._color_fill_loose_highlight, outline=self._color_outline_loose_highlight, width=1.0*zoomlevel)
        else:
            if self._type == SMANodeType.SOLID:
                roundPolygon(self._canvas, [location[0]-self._size, location[0]-self._size, location[0]+self._size, location[0]+self._size], [location[1]-self._size, location[1]+self._size, location[1]+self._size, location[1]-self._size], 10, width=1.0*zoomlevel, outline=self._color_outline, fill=self._color_fill)
            elif self._type == SMANodeType.ELASTIC:
                dID = roundPolygon(self._canvas, [self.getLocation()[0]-self._size, self.getLocation()[0]-self._size, self.getLocation()[0]+self._size, self.getLocation()[0]+self._size], [self.getLocation()[1]-self._size, self.getLocation()[1]+self._size, self.getLocation()[1]+self._size, self.getLocation()[1]-self._size], 2, width=0, outline=self._color_outline, fill=self._color_fill)
                self._canvas.lower(dID)
                roundPolygon(self._canvas, [location[0]-self._size, location[0]-self._size, location[0]+self._size, location[0]+self._size], [location[1]-self._size, location[1]+self._size, location[1]+self._size, location[1]-self._size], 2, width=1.0*zoomlevel, outline=self._color_outline, fill=self._color_fill)
            else:
                self._id = self._canvas.create_oval(location[0]-self._size, location[1]-self._size, location[0]+self._size, location[1]+self._size, fill=self._color_fill_loose, outline=self._color_outline_loose, width=1.0*zoomlevel)

        if self._displayPin:
            pintext = "PIN\n" + str(self.getPin()+1)
            self._canvas.create_text(location[0], location[1], anchor=CENTER, font=("Verdana", int(3*zoomlevel), "bold"), text=pintext, fill="#12333D", justify = CENTER)

    def isInBounds(self, x, y):
        return getDistance([x,y], self._location) <= self._size

    def setType(self, type):
        self._type = type

    def getType(self):
        return self._type

    def setMovable(self, movable):
        self._resetToEMA = not movable

    def displayBounds(self, enabled):
        self._displayBounds = enabled

    def calculateNewPosition(self, step):
        if self.getType() == SMANodeType.LOOSE:
            before = self._oldlocation.copy()
            self._oldlocation[0] = self._location[0]
            self._oldlocation[1] = self._location[1]
            self._location[0] = ((2*self._location[0] - before[0])/1000 + self._acceleration[0]*step**2)*1000
            self._location[1] = ((2*self._location[1] - before[1])/1000 + self._acceleration[1]*step**2)*1000

        self._velocity[0] = ((self._location[0]-self._oldlocation[0])/ 1000) / (step)
        self._velocity[1] = ((self._location[1]-self._oldlocation[1])/ 1000) / (step)

    def calculateNewAcceleration(self):
        localnetforce = [0,0]

        if self.getType() == SMANodeType.LOOSE:
            for c in self._connections:
                springForce = c.getSpringForce(self)
                localnetforce[0] += springForce[0]
                localnetforce[1] += springForce[1]

            self._acceleration[0] = localnetforce[0] / self._mass
            self._acceleration[1] = localnetforce[1] / self._mass

    def getVelocity(self):
        return self._velocity

    def getMass(self):
        return self._mass

    def resetSimulation(self):
        self._velocity = [0, 0]
        self._acceleration = [0, 0]
        self._originLocation = self._location.copy()
        self._oldlocation = self._location.copy()
        global globalvars
        self._mass = globalvars.sma_mass

    def resetToOriginLocation(self):
        self._location = self._originLocation.copy()

    def setPin(self, pin):
        self._pin = pin

    def getPin(self):
        return self._pin

    def assignSkinNodes(self, skinNodes):
        self._skinNodes = []
        self._skinNodes = skinNodes

        # set centroid center
        self._initcenter = self._getCenterOfAssignedSkinNodes()

    def updateSkinNodeForce(self):
        if len(self._skinNodes) > 0:
            force = [0,0]

            for c in self._connections:
                springForce = c.getSpringForce(self)
                force[0] += springForce[0]
                force[1] += springForce[1]

            force[0] = force[0] / len(self._skinNodes)
            force[1] = force[1] / len(self._skinNodes)

            for s in self._skinNodes:
                s.setDraggingForce(force)

    def _getCenterOfAssignedSkinNodes(self):
        allPoints = []

        for s in self._skinNodes:
            allPoints.append(s.getLocation())

        return self._getCentroid(allPoints)

    def _getCentroid(self, points):
        x = 0
        y = 0

        for p in points:
            x += p[0]
            y += p[1]

        x = x / len(points)
        y = y / len(points)

        return [x, y]

    def getAllNeighbourNodes(self):
        nodes = []
        for c in self._connections:
            nodes.append(c.getOtherNode(self))
        return nodes

    def updatePosition(self):
        if self.getType() == SMANodeType.ELASTIC and len(self._skinNodes) > 0:
            newcenter = self._getCenterOfAssignedSkinNodes()
            self._oldlocation = self._location.copy()
            self._location = [self._originLocation[0]+(newcenter[0]-self._initcenter[0]), self._originLocation[1]+(newcenter[1]-self._initcenter[1])]

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_canvas']
        del state['_RenderingObject__view']
        del state['_skinNodes']

        return state
