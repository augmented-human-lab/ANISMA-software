from components.Connection import *
from util.util import *
from util.globalvars import *

class SkinSpring(Connection):

    def __init__(self, canvas, nodeA, nodeB):
        super().__init__(canvas, nodeA, nodeB, width=1)
        self._restingLength = getDistance(nodeA.getLocation(), nodeB.getLocation())
        self._diagonal = False

        global globalvars
        self._springConst = globalvars.skin_sprinconstant
        self._dampingconst = globalvars.skin_damping
        if self._diagonal:
            self._springConst = globalvars.skin_sprinconstant_diag
            self._dampingconst = globalvars.skin_damping_diag

        self._highlight = False
        self._color = "#CCCCCC"
        self._linewidth = 2

    def setDiagonal(self, enabled):
        self._diagonal = enabled

    def isDiagonal(self):
        return self._diagonal

    def setRestingLength(self, val):
        self._restingLength = val

    def update(self, zoomlevel):

        if not self._diagonal:
            # draw underlying grid white
            startLocation = self._nodes[0].getAnchorLocation()
            endLocation = self._nodes[1].getAnchorLocation()
            self.__id = self._canvas.create_line(startLocation[0], startLocation[1], endLocation[0], endLocation[1], fill="#FFFFFF", width=2, joinstyle=ROUND, capstyle=ROUND, tags="level-5")

            # draw above the animated mesh
            if self._highlight:
                super().update(2)
            else:
                super().update(1)

    def setSpringConst(self, const):
        self._springConst = const

    def setHighlighted(self, enabled):
        self._highlight = enabled
        if enabled:
            self._color = "#FAA"
            self._linewidth = 4
        else:
            self._color = "#CCCCCC"

    def getSpringConstant(self):
        return self._springConst

    def _getDampingForce(self, forNode):
        vela = [0,0]
        velb = [0,0]

        if forNode == self._nodes[0]:
            vela = self._nodes[0].getVelocity()
            velb = self._nodes[1].getVelocity()
        else:
            vela = self._nodes[1].getVelocity()
            velb = self._nodes[0].getVelocity()

        # critically damped, adjusted springlength scaling for different meshresolution
        damping = self._dampingconst#1.824# 0.5#
        dampingforce = [0,0]
        dampingforce[0] = damping*(vela[0] - velb[0])
        dampingforce[1] = damping*(vela[1] - velb[1])

        return dampingforce

    def getRestingLength(self):
        if not self._diagonal:
            return self._restingLength * (6/5)
        else:
            return self._restingLength * (6/7)

    def getSpringForce(self, forNode):
        global globalvars
        self._springConst = globalvars.skin_sprinconstant#24.3748*10 #
        self._dampingconst = globalvars.skin_damping
        if self._diagonal:
            self._springConst = globalvars.skin_sprinconstant_diag / self.getRestingLength()
            self._dampingconst = globalvars.skin_damping_diag / self.getRestingLength()
        currentLength = getDistance(self._nodes[0].getLocation(), self._nodes[1].getLocation())
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

        restLength = self.getRestingLength()
        displacement = springconst * (restLength-currentLength) / 1000
        dampingforce = self._getDampingForce(forNode)

        return [-dirVec[0]*displacement-dampingforce[0], -dirVec[1]*displacement-dampingforce[1]]
