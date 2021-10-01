
class SMAWireParameters:

    def __init__(self, wireDiameter_mm, wireResistancePerMeter, length_mm):
        self._wireDiameter = wireDiameter_mm
        self._resistanceFactor = wireResistancePerMeter
        self._wireLength = length_mm

    def getWireDiameter(self):
        return self._wireDiameter

    def getResistanceFactor(self):
        return self._resistanceFactor

    def setWireLength(self, length):
        self._wireLength = length

    def getWireLength(self):
        return self._wireLength

    def getResistance(self):
        return self.getWireLength()/1000 * self._resistanceFactor

    def getInfo(self):
        text  = "wire diameter: " + str(round(self.getWireDiameter(),2)) + "mm\n"
        text += "wire length: " + str(round(self.getWireLength(),2)) + "mm\n\n"
        text += "resistance: " + str(round(self.getResistance(),2)) + "Ohms\n"

        return text


    def __eq__(self, other):
        if not isinstance(other, SMAWireParameters):
            return NotImplemented

        return self._wireDiameter == other._wireDiameter and self._resistanceFactor == other._resistanceFactor and self._wireLength == other._wireLength
