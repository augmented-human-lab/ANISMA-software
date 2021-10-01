from tkinter import *
from render.RenderingObject import *
from components.Connection import Connection
from simulation.Model import *
from util.util import *
from util.drawUtil import *
from util.globalvars import *
from components.SMANodeType import SMANodeType

class SMAConnection(Connection):

    _parameters = None
    _currentLength = 0
    _constraints = []
    _color = "#3F4A56"
    _color_highlighted = "#BBB"
    _hasError = False
    _lastError = ""
    _tension = 0.0
    _nodeDiameter = 10

    def __init__(self, canvas, nodeA, nodeB, parameters, constraints=[], name=""):
        super().__init__(canvas, nodeA, nodeB)

        self._constraints = constraints
        for c in constraints:
            c.setOwner(self)

        self._name = name
        self._parameters = parameters
        self._maxForce = getUpperForceLimit(getMaxPower(self.getSMAParameters()), self.getSMAParameters())
        global globalvars
        self._dampingconst = globalvars.sma_damping# 0.1
        self._displayLength = True
        self._displayName = False
        self._phase = 0

    def displayLength(self,enabled):
        self._displayLength = enabled

    def displayName(self,enabled):
        self._displayName = enabled

    def checkConstraints(self):
        self._hasError = False
        for c in self._constraints:
            if not c.isSatisfied():
                self._lastError = "Error: " + c.getDescription()
                self._hasError = True

        if self._hasError:
            self._color = "#FD1766"
        else:
            self._color = "#3F4A56"

    def __updateLength(self):
        self._currentLength = getDistance(self._nodes[0].getLocation(), self._nodes[1].getLocation())

    def __drawSpring(self, zoomlevel, color='black'):
        nodePosA = self._nodes[0].getLocation()
        nodePosB = self._nodes[1].getLocation()
        drawConnectionWithParams(self._canvas, nodePosA, nodePosB, self._parameters, zoomlevel, color=color, tension=self._tension)

    def __drawLimits(self, zoomlevel):
        nodePosA = self._nodes[0].getLocation()
        nodePosB = self._nodes[1].getLocation()

    def update(self, zoomlevel):
        self.__updateLength()
        self.checkConstraints()

        if self.isHighlighted:
            self.__drawSpring(zoomlevel, color=self._color_highlighted)
            self.__drawLimits(zoomlevel)
        else:
            self.__drawSpring(zoomlevel, color=self._color)


        if self._hasError:
            self._color = "#FD1766"
        else:
            self._color = "#3F4A56"

        if self._displayName:
            self._drawSpringLabel(self.getName(),zoomlevel)
        if self._displayLength:
            lengthstr = str(self.getContractionFraction())+"%"
            self._drawSpringLabel(lengthstr,zoomlevel, dy=0, color=self._color)

    def getContractionFraction(self):
        return int(round(100*(1-(self._currentLength-self.getMinLength()) / (self.getMaxLength()-self.getMinLength())),0))

    def getMaxLength(self):
        return self._parameters.getExtendedLength()+self._nodeDiameter # including node diameter

    def getMinLength(self):
        return self._parameters.getContractedLength()+self._nodeDiameter # including node diameter

    def hasError(self):
        return self._hasError

    def getLastError(self):
        return self._lastError

    def setTension(self, tension):
        self._tension = tension

    def getTension(self):
        return self._tension

    def setMaxForce(self, force):
        self._maxForce = force

    def getMaxForce(self):
        return self._maxForce

    def getPullForce(self):
        return self._tension * self.getMaxForce()

    def getName(self):
        return self._name

    def getSMAParameters(self):
        return self._parameters

    def setSMAParameters(self, params):
        self._parameters = params
        self._maxForce = getUpperForceLimit(getMaxPower(self.getSMAParameters()), self.getSMAParameters())

    def getSpringConstant(self):
        maxpower = getMaxPower(self._parameters)
        ratedForce = getForce(2000, maxpower, self._parameters)
        return ratedForce*self._tension

    def _getDampingForce(self, forNode, springconst):
        vela = [0,0]
        velb = [0,0]

        if forNode == self._nodes[0]:
            vela = self._nodes[0].getVelocity()
            velb = self._nodes[1].getVelocity()
        else:
            vela = self._nodes[1].getVelocity()
            velb = self._nodes[0].getVelocity()

        # critically damped, adjusted springlength scaling for different meshresolution
        global globalvars
        self._dampingconst = 2*math.sqrt((globalvars.skin_mass)*springconst) #sma_damping
        self._dampingconst = globalvars.sma_damping
        if self._parameters.getSpringDiameter() == 2.54:
            self._dampingconst = 0.005

        damping = self._dampingconst

        dampingforce = [0,0]
        dampingforce[0] = damping*(vela[0] - velb[0])
        dampingforce[1] = damping*(vela[1] - velb[1])
        return dampingforce

    def getSpringForce(self, forNode):

        self.__updateLength()
        springconst = self.getSpringConstant()

        dirVec = [0, 0]
        aPos = [0, 0]
        bPos = [0, 0]

        if forNode == self._nodes[0]:
            aPos = self._nodes[0].getLocation()
            bPos = self._nodes[1].getLocation()
        else:
            bPos = self._nodes[0].getLocation()
            aPos = self._nodes[1].getLocation()

        dirVec[0] = bPos[0] - aPos[0]
        dirVec[1] = bPos[1] - aPos[1]

        mag = magnitude(dirVec)
        dirVec = [dirVec[0]/mag, dirVec[1]/mag]

        displacement = (self.getMinLength()-self._currentLength ) 

        x = -(self.getMinLength()-self._currentLength) 
        force = self.getPullForce() / self.getMaxLength() / 1000 * globalvars.smapoweramplifier  

        if self.hasLooseNode():
            force = force / 3

        dampingforce = self._getDampingForce(forNode, force)
        return [-dirVec[0]*force*displacement-dampingforce[0], -dirVec[1]*force*displacement-dampingforce[1]]

    def _drawSpringLabel(self, text, zoomlevel, dy=0, color="#3F4A56"):
        # display distance
        taillength = 5+dy
        dist = getDistance(self._nodes[0].getLocation(), self._nodes[1].getLocation())
        ddir = getUnitVec([self._nodes[1].getLocation()[0]-self._nodes[0].getLocation()[0], self._nodes[1].getLocation()[1]-self._nodes[0].getLocation()[1]])
        norm = [-ddir[1], ddir[0]]
        font = ("Verdana", int(3*zoomlevel))
        mid = [self._nodes[0].getLocation()[0] + ddir[0]*dist/2, self._nodes[0].getLocation()[1] + ddir[1]*dist/2]

        if self._nodes[0].getLocation()[1] - self._nodes[1].getLocation()[1] > 0:
            rotation = -angleBetween(getUnitVec([-1,0]), ddir)
        else:
            rotation = angleBetween(getUnitVec([-1,0]), ddir)

        rotation = (rotation-180)
        if self._nodes[0].getLocation()[0] - self._nodes[1].getLocation()[0] > 0 or dist == 0 :
            rotation = (rotation-180)
            mid = [mid[0]+norm[0]*taillength, mid[1]+norm[1]*taillength]
        else:
            mid = [mid[0]-norm[0]*taillength, mid[1]-norm[1]*taillength]

        self._canvas.create_text(mid[0], mid[1], anchor=CENTER, angle=rotation,font=font, text=text, justify=CENTER, fill=color)

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['_canvas']
        del state['_RenderingObject__view']

        return state

    def resetPhases(self):
        self._phases = []

    def assignPhase(self, phase):
        self._phases.append(phase)

    def getPhases(self):
        return self._phases

    def hasLooseNode(self):
        return (self._nodes[0].getType() == SMANodeType.LOOSE) or (self._nodes[1].getType() == SMANodeType.LOOSE)
