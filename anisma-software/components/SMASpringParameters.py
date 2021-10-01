import math
from components.SMAWireParameters import SMAWireParameters

def getOptimalCoilNumber(params, length, smacontraction=0):
    SR = (params.getHotSpringRatio() + (params.getCoolSpringRatio() - params.getHotSpringRatio())*(1.0-smacontraction))
    solidLength = length / SR
    return solidLength / params.getWireDiameter()

class SMASpringParameters(SMAWireParameters):

    def __init__(self, wireDiameter_mm, wireResistancePerMeter, springDiameter_mm, hotSR, coolSR, coilNumber):
        solidWireLength = math.pi * (springDiameter_mm-wireDiameter_mm) * coilNumber
        super().__init__(wireDiameter_mm, wireResistancePerMeter, solidWireLength)
        self._hotSR = hotSR
        self._coolSR = coolSR
        self._coilNumber = coilNumber
        self._springDiameter = springDiameter_mm

    def _updateParams(self):
        solidWireLength = math.pi * (self._springDiameter-super().getWireDiameter()) * self._coilNumber
        super().setWireLength(solidWireLength)

    def getSolidLength(self):
        return self._coilNumber * self.getWireDiameter()

    def getExtendedLength(self):
        return self.getSolidLength() * self._coolSR

    def getCoolLength(self):
        return self.getExtendedLength()

    def getContractedLength(self):
        return self.getSolidLength() * self._hotSR

    def getHotLength(self):
        return self.getContractedLength()

    def getSpringDiameter(self):
        return self._springDiameter

    def setNumberOfCoils(self, number):
        self._coilNumber = number
        self._updateParams()

    def getNumberOfCoils(self):
        return self._coilNumber

    def getCoolSpringRatio(self):
        return self._coolSR

    def getHotSpringRatio(self):
        return self._hotSR

    def getInfo(self):
        text  = super().getInfo()
        text += "coils: " + str(round(self.getNumberOfCoils(),2)) + "\n\n"
        text += "spring diameter: " + str(round(self.getSpringDiameter(),2)) + "mm\n"
        text += "solid spring length: " + str(round(self.getSolidLength(),2)) + "mm\n"
        text += "min spring length: " + str(round(self.getContractedLength(),2)) + "mm\n"
        text += "max spring length: " + str(round(self.getExtendedLength(),2)) + "mm\n"

        return text

    def __eq__(self, other):
        if not isinstance(other, SMASpringParameters):
            return NotImplemented

        return self._hotSR == other._hotSR and self._coolSR == other._coolSR and self._coilNumber == other._coilNumber and self._springDiameter == other._springDiameter
