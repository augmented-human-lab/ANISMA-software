from components.constraints.SMAConstraint import SMAConstraint
from components.SMANodeType import *

class SMAConstraint_NoSingleLooseNode(SMAConstraint):

    def getDescription(self):
        return "A loose node must have at least two connections."

    def isSatisfied(self):
        for n in self._smaObj.getNodes():
            if n.getType() is SMANodeType.LOOSE:
                if len(n.getConnections()) <= 1:
                    return False

        return True
