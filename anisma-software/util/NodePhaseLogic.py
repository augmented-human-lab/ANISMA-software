
class NodePhaseLogic():

    def __init__(self):
        self._phases = [1,2,3,4]

    def resetPhases(self):
        self._phases = [1,2,3,4]

    def getAvailablePhases(self):
        return self._phases

    def consumePhase(self, phase):
        self._phases.remove(phase)
