from components.constraints.SMAConstraint import SMAConstraint

class SMAConstraint_MaxLength(SMAConstraint):

    def getDescription(self):
        return "Exceeded maximal SMA stretch length"

    def isSatisfied(self):
        return self._smaObj.getContractionFraction() >= -5
