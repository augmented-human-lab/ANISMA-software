

class AMNodeState():

    def __init__(self, node, position):
        self._node = node
        self._pos = position
        self._frame = None

    def getNode(self):
        return self._node

    def getPosition(self):
        return self._pos

    def getFrame(self):
        return self._frame

    def setFrame(self, frame):
        self._frame = frame
