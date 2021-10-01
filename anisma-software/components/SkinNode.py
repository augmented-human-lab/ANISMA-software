from components.Node import *
from util.util import *
from util.globalvars import *

class SkinNode(Node):

    def __init__(self, canvas, springRestingLength):
        super().__init__(canvas, diameter=1)
        self._restingLength = springRestingLength

        self._newlocation = [0, 0]
        self._velocity = [0, 0]
        self._acceleration = [0, 0]
        self._mass = 0
        self._fixed = False
        self._draggingForce = [0,0]
        self._anchorLocation = [0,0]
        self._highlight = False
        global globalvars
        self._stiffness = globalvars.collisionconstraint

    def update(self, zoomlevel):
        if self._highlight:
            super().update(zoomlevel)
        else:
            pass

    def setHighlighted(self, enabled):
        self._highlight = enabled

    def setStiffness(self, stiffness):
        self._stiffness = stiffness

    def setDraggingForce(self, force):
        self._draggingForce = [force[0], force[1]]

    def isFixed(self):
        return self._fixed

    def setFixed(self, fixed):
        self._fixed = fixed

        if self._fixed:
            self._color_fill = "#FF0000"

    def applyConstraints(self):
        global globalvars
        for i in range(1):
            for c in self._connections:
                if c.isDiagonal():
                    otherNode = c.getOtherNode(self)
                    p0 = self.getLocation()
                    p1 = otherNode.getLocation()
                    dist = getDistance(p0, p1)
                    diff = (dist - c.getRestingLength())/dist

                    correctionFactor = max(globalvars.collisionconstraint,self._stiffness)
                    self.setLocation(p0[0] + (p1[0]-p0[0])/dist * correctionFactor * diff, p0[1] + (p1[1]-p0[1])/dist * correctionFactor * diff)

    def calculateNewPosition(self, step):
        before = self._oldlocation.copy()
        self._oldlocation[0] = self._location[0]
        self._oldlocation[1] = self._location[1]
        self._location[0] = ((2*self._location[0] - before[0])/1000 + self._acceleration[0]*step**2)*1000
        self._location[1] = ((2*self._location[1] - before[1])/1000 + self._acceleration[1]*step**2)*1000
        if not self.isFixed():
            self.applyConstraints()
        self._velocity[0] = ((self._location[0]-before[0]) / 1000) / (step) # m/s
        self._velocity[1] = ((self._location[1]-before[1]) / 1000) / (step) #

    def getDampingFactor(self, sprinconstant, mass):
        return 2*math.sqrt(sprinconstant*mass)

    def calculateNewAcceleration(self):
        localnetforce = [0,0]

        if not self._fixed:
            for c in self._connections:
                springForce = c.getSpringForce(self)
                localnetforce[0] += springForce[0]
                localnetforce[1] += springForce[1]

            anchorForce = self.getAnchorSpringForce()
            localnetforce[0] += anchorForce[0]
            localnetforce[1] += anchorForce[1]

            # dragging force includes SMA Spring force
            localnetforce[0] += self._draggingForce[0]
            localnetforce[1] += self._draggingForce[1]

            self._acceleration[0] = localnetforce[0] / self._mass
            self._acceleration[1] = localnetforce[1] / self._mass

    def getVelocity(self):
        return self._velocity

    def getMass(self):
        return self._mass

    def getAnchorLocation(self):
        return self._anchorLocation

    def resetSimulation(self):
        self._velocity = [0, 0]
        self._acceleration = [0, 0]
        self._anchorLocation = self._location.copy()
        self._oldlocation = self._location.copy()

        massdensity = math.sqrt(0.0102)**2
        volelements = 8
        elementvolume = self._restingLength**2
        global globalvars
        self._mass = globalvars.skin_mass

    def resetToOriginLocation(self):
        self._location = self._anchorLocation.copy()

    def getAnchorSpringForce(self):
        global globalvars
        anchorSpringConst = globalvars.anchor_sprinconstant

        damping = globalvars.anchor_damping

        dirVec = [0, 0]
        aPos = self.getLocation()
        bPos = self._anchorLocation
        vela = self.getVelocity()
        dirVec[0] = (aPos[0] - bPos[0]) / 1000 # in meteres
        dirVec[1] = (aPos[1] - bPos[1]) / 1000 # in meteres
        return [-anchorSpringConst * dirVec[0] -damping*(vela[0] - 0), -anchorSpringConst *dirVec[1] -damping*(vela[1] - 0)]
