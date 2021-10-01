class AMTrack():

    def __init__(self, sma):
        self._sma = sma
        self._clips = []
        self._highlighted = False

    def setHighlighted(self, enabled):
        self._highlighted = enabled

    def isHighlighted(self):
        return self._highlighted

    def getSMA(self):
        return self._sma

    def sortClips(self):
        getTimeOfClip = lambda f: f.getStartTime()
        self._clips.sort(key=getTimeOfClip)

    def addClip(self, clip):
        self._clips.append(clip)
        self.sortClips()
        clip.setTrack(self)

    def removeClip(self, clip):
        if clip in self._clips:
            self._clips.remove(clip)

        self.sortClips()

    def getClips(self):
        return self._clips
