from animation.AMNodeState import *

"""
An animation frame keeps track of the positions of a set of nodes to a given time.
"""
class AMFrame():

    def __init__(self, time):
        self._time = time
        self._nodeStates = []

    def getTime(self):
        return self._time

    def getNodeStates(self):
        return self._nodeStates

    def _getNodeStateFor(self, node):
        for s in self._nodeStates:
            if s.getNode() is node:
                return s

        return None

    def setTime(self, time):
        self._time = time

    def setNodeState(self, nodeState):
        existingNState = self._getNodeStateFor(nodeState.getNode())

        if existingNState is not None:
            self._nodeStates.remove(existingNState)

        nodeState.setFrame(self)
        self._nodeStates.append(nodeState)

    def printStates(self):
        pos = []

        for ns in self._nodeStates:
            pos.append(ns.getPosition())

        return (pos)
