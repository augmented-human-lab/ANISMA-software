from animation.AMNodeState import *
from simulation.Model import *

"""
An animation frame keeps track of the positions of a set of nodes to a given time.
"""
class AMClip():

    def __init__(self, startTime, power, actuationDuration, sma):
        self._startTime = startTime
        self._power = power
        self._actuationDuration = actuationDuration
        self._drawingPath = []
        self._track = None
        self._actuating = False
        self._sma = sma

        self._calculateSignalPath()


    def _calculateSignalPath(self):
        self._drawingPath = []

        # draw signal
        maxIntensity = getUpperForceLimit(getMaxPower(self._sma.getSMAParameters()), self._sma.getSMAParameters())
        power = getMinPower() + self._power * (getMaxPower(self._sma.getSMAParameters()) - getMinPower())

        duration = self._actuationDuration
        releaseTime = getRelaxTime(5, duration, power, self._sma.getSMAParameters())
        self._totalDuration = self._actuationDuration + releaseTime

        maxTime = self._totalDuration
        duration = self._actuationDuration

        step = 100
        prevPoint = [0, 0]
        self._drawingPath.append(prevPoint)

        # create rising signal
        force = 0
        for i in range(int(duration/step)):
            time = i * step
            force = getForce(time, power, self._sma.getSMAParameters())
            x = max(0, min(1, time/maxTime))
            y = max(0, min(1, force/maxIntensity))
            nextPoint = [x, y]
            self._drawingPath.append(nextPoint)

        # create falling signal
        for i in range(int((maxTime-duration)/step)):
            time = i * step
            force = getRelaxForce(time, duration, power, self._sma.getSMAParameters())
            x = max(0, min(1, (duration + time)/maxTime))
            y = max(0, min(1, force/maxIntensity))
            nextPoint = [x, y]
            self._drawingPath.append(nextPoint)

    def getIntensity(self, time):
        power = getMinPower() + self._power * (getMaxPower(self._sma.getSMAParameters()) - getMinPower())
        upperLimit = getUpperForceLimit(getMaxPower(self._sma.getSMAParameters()),self._sma.getSMAParameters())

        if time < self._actuationDuration:
            return min(1.0, max(0.0, getForce(time, power, self._sma.getSMAParameters()) / upperLimit))
        else:
            return min(1.0, max(0.0, getRelaxForce(time-self._actuationDuration, self._actuationDuration, power, self._sma.getSMAParameters()) / upperLimit))

    def getDrawingPath(self):
        return self._drawingPath

    def getStartTime(self):
        return self._startTime

    def getPower(self):
        return self._power

    def getActuationDuration(self):
        return self._actuationDuration

    def getTotalDuration(self):
        return self._totalDuration

    def setStartTime(self, time):
        self._startTime = time

    def setPower(self, power):
        self._power = power
        self._calculateSignalPath()

    def setActuationDuration(self, duration):
        self._actuationDuration = duration
        self._calculateSignalPath()

    def setTrack(self, track):
        self._track = track

    def getTrack(self):
        return self._track

    def setActuatingOn(self, enabled):
        self._actuating = enabled

    def isActuating(self):
        return self._actuating
