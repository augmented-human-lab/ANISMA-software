from components.constraints.Constraint import Constraint

class SMAConstraint(Constraint):

    _smaObj = None

    def setOwner(self, smaObj):
        self._smaObj = smaObj
