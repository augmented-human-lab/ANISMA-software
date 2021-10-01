import random

class SkinLayer():

    def __init__(self):
        self._skinnodes = []
        self._skinsprings = []

    def getSkinNodes(self):
        return self._skinnodes

    def getSkinSprings(self):
        return self._skinsprings

    def addSkinNode(self, skinnode):
        self._skinnodes.append(skinnode)

    def addSkinSpring(self, skinspring):
        self._skinsprings.append(skinspring)

    def calculateNewPositions(self, stepsize):
        random.shuffle(self._skinnodes)
        for n in self._skinnodes:
            n.calculateNewPosition(stepsize)

    def calculateNewAccelerations(self):
        for n in self._skinnodes:
            n.calculateNewAcceleration()

    def resetAllPositions(self):
        for n in self._skinnodes:
            n.resetToOriginLocation()

    def resetSimulation(self):
        for n in self._skinnodes:
            n.resetSimulation()

    def removeSkinNode(self, node):
        self._skinnodes.remove(node)

    def removeSkinSpring(self, conn):
        if conn in self._skinsprings:
            self._skinsprings.remove(conn)

    def randomize(self):
        random.shuffle(self._skinsprings)
