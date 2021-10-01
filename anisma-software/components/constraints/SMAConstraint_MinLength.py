from components.constraints.SMAConstraint import SMAConstraint
from util.globalvars import *

class SMAConstraint_MinLength(SMAConstraint):

    def getDescription(self):
        return "Exceeded minimal SMA length"

    def isSatisfied(self):
        global globalvars

        if globalvars.simulationRunning:
            return True
        else:
            return self._smaObj.getContractionFraction() <= 105
