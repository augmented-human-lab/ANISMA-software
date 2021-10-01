from util.drawUtil import *
from animation.AMFrame import *
from animation.AMNodeState import *
from components.SMANodeType import SMANodeType
from animation.AMScene import *
from animation.AMUtilities import *
from components.SkinLayerFactory import *
from animation.AMTrack import AMTrack
from components.SMANode import SMANode
from components.SMASpringParameters import SMASpringParameters
import time
from time import sleep
from threading import Timer
from threading import Thread
from util.util import *
from util.globalvars import *

class AMScene():

    def __init__(self, controller, skinLayer, printLayer):
        self._controller = controller
        self._skinLayer = skinLayer
        self._printLayer = printLayer
        self._tracks = []
        self._smas = []
        self._frames = []
        self._recordedNodes = []
        self._currentTime = 0
        self._maxTime = 2 * 60 * 1000
        self._currentFrame = None
        self._playThread = None
        self._mainview = None
        self._timelineview = None
        self._window = None
        self._resetTime = False

        self._startTime = 0
        self._lastTime = 0
        self._count = 0
        self._animStep = 1
        self._stop = True
        self._maxClipTime = 0

        self._controllerBoardActive = False

        self._animationRanWithError = False
        self._animHasRun = False

    def setControllerBoardActive(self, enabled):
        self._controllerBoardActive = enabled

    def _getAllNodes(self):
        nodes = []
        objs = self._mainview.getAllObjects()

        for o in objs:
            if isinstance(o, SMANode):
                nodes.append(o)

        return nodes

    def assignSkinNodesToSMANodes(self):
        nodes = self._getAllNodes()

        for n in nodes:
            if n.getType() == SMANodeType.ELASTIC:
                assignNodes = []
                locA = n.getLocation()
                for s in self._skinLayer.getSkinNodes():
                    s.setDraggingForce([0,0])
                    locB = s.getLocation()
                    if getDistance(locA, locB) <= 10:
                        assignNodes.append(s)
                n.assignSkinNodes(assignNodes)

    def clearOldSkinMesh(self):
        nodestoremove = []
        if self._skinLayer is not None:
            for s in self._skinLayer.getSkinNodes():
                self._mainview.remove(s, recurse=False, update=False, deleteConnections=True)
                nodestoremove.append(s)
        for n in nodestoremove:
            for c in n.getConnections():
                self._skinLayer.removeSkinSpring(c)
            self._skinLayer.removeSkinNode(n)

    def prepareSkinMesh(self):
        global globalvars

        self.clearOldSkinMesh()
        self._skinLayer = createNewSkinLayer(self._mainview, [-110, -110], [110, 110], 10)#7.5)
        nodes = self._getAllNodes()
        nodestoremove = []
        areabuffer = 40

        for s in self._skinLayer.getSkinNodes():
            found = False
            for n in nodes:
                locA = n.getLocation()
                locB = s.getLocation()
                if getDistance(locA, locB) < areabuffer:
                    found = True

            if not found and not self._printLayer.isInPrintArea(s.getLocation(), areabuffer):
                nodestoremove.append(s)
            else:
                if self._printLayer.isInPrintArea(s.getLocation(), 5):
                    conns = s.getConnections()
                    for c in conns:
                        otherNode = c.getOtherNode(s)
                        if self._printLayer.isInPrintArea(otherNode.getLocation(), 5):
                            thickness = self._printLayer.getThicknessAtPoint(otherNode.getLocation(), 5)

                            # map print thickness to skin stiffnes to max print layer
                            stiffness = mapVal(thickness, 0.0, 1.0, globalvars.collisionconstraint+1, globalvars.collisionconstraint_dist+1)

                            c.setHighlighted(True)
                            otherNode.setStiffness(stiffness)
                            s.setStiffness(stiffness)

        for n in nodestoremove:
            self._skinLayer.removeSkinNode(n)
            for c in n.getConnections():
                c.getOtherNode(n).setFixed(True) # Fix the nodes at the border
                self._skinLayer.removeSkinSpring(c)
            self._mainview.remove(n, recurse=False, update=False, deleteConnections=True)

    def nextSimulationStep(self):
        nodes = self._getAllNodes()
        step = self._animStep/1000

        for n in nodes:
            n.calculateNewPosition(step)
        self._skinLayer.calculateNewPositions(step)

        for n in nodes:
            n.updatePosition()

        for n in nodes:
            n.updateSkinNodeForce()

        for n in nodes:
            n.calculateNewAcceleration()
        self._skinLayer.calculateNewAccelerations()


    def _playing(self):
        newtime = time.time() * 1000
        if not self._stop and newtime - self._startTime >= self._animStep*self._count :
            self._count += 1

            self._checkIfAnimationHasRun()
            self.checkClipActuation()
            self.setSceneTime(min(newtime - self._startTime, self._maxTime))
            self.nextSimulationStep()

            if newtime - self._lastTime > 33:
                self.updateAllViews()
                self._lastTime = newtime

        if self._stop == False and self._currentTime <= self._maxTime:
            self._window.after(1, self._playing)
        elif self._resetTime:
            self.setSceneTime(0)
            self.updateAllViews()

    def checkClipActuation(self):
        if self._controllerBoardActive:
            clips = self.getClips()


            actuationCommands = []

            for c in clips:
                if self._currentTime >= c.getStartTime() and self._currentTime < c.getStartTime() + c.getActuationDuration():
                    if not c.isActuating():
                        clip_sma = c.getTrack().getSMA()

                        actuationCommands.append([clip_sma, c.getPower(), c.getActuationDuration()])
                        c.setActuatingOn(True)
                else:
                    if c.isActuating():
                        # manual disabling power not necessary with new protocol
                        c.setActuatingOn(False)

            # collectively set power settings and try to save overhead
            if len(actuationCommands) > 0:
                self._controller.initPowerSettings()

                for ac in actuationCommands:
                    self._controller.setSMAPower(ac[0], ac[1], ac[2])

                self._controller.flushPowerSettings()

    def setTimelineView(self, timelineview):
        self._timelineview = timelineview

    def setMainView(self, mainview):
        self._mainview = mainview

    def setWindow(self, window):
        self._window = window

    def _getFrameAtTime(self, time):
        for f in self._frames:
            if f.getTime() is time:
                return f

        return None

    def addFrame(self, frame):

        self._frames.append(frame)
        getTimeOfFrame = lambda f: f.getTime()
        self._frames.sort(key=getTimeOfFrame)

    def getTrackFor(self, sma):
        for t in self._tracks:
            if t.getSMA() == sma:
                return t

        return None

    def addTrackForSMA(self, sma):
        track = self.getTrackFor(sma)

        if track is None:
            track = AMTrack(sma)
            self._tracks.append(track)

        if self._timelineview is not None:
            self._timelineview.updateView()

    def removeTrackForSMA(self, sma):
        track = self.getTrackFor(sma)

        if track is not None:
            self._tracks.remove(track)

        if self._timelineview is not None:
            self._timelineview.updateView()

    def removeClip(self, clip):
        track = clip.getTrack()

        if track is not None:
            track.removeClip(clip)

        self.updateAllViews()

    def addClip(self, clip, sma):
        track = self.getTrackFor(sma)

        if track is None:
            track = AMTrack(sma)
            track.addClip(clip)
            self._tracks.append(track)
        else:
            track.addClip(clip)

        self.updateAllViews()

    def removeFrame(self, frame):
        self._frames.remove(frame)

    def getFrames(self):
        return self._frames

    def getTracks(self):
        return self._tracks

    def setTracks(self, tracks):
        self._tracks = tracks

    def getClips(self):
        clips = []
        for t in self._tracks:
            clips +=  t.getClips()

        return clips

    def setSceneTime(self, time):
        self._currentTime = int(time)
        self._currentFrame = self._getFrameAtTime(int(time))
        self.updateSceneObjects()

    def jumpToFrame(self, frame):
        self._currentTime = frame.getTime()
        self._currentFrame = frame
        self.updateSceneObjects()

    def _getNextPos(self, nextFrame, nsB):
        for nsA in nextFrame.getNodeStates():
            if nsA.getNode() is nsB.getNode():
                return nsA.getPosition()

        return None

    def updateSceneObjects(self):
        for n in self._recordedNodes:
            if self._currentFrame is not None and getNodeStateFromFrame(self._currentFrame, n) is not None:
                # If there is a frame containing the state for the note at the current scene time
                # -> just set the state accordingly
                ns = getNodeStateFromFrame(self._currentFrame, n)
                pos = ns.getPosition()
                n.setLocation(pos[0], pos[1])
            else:
                # Else we have to interpolate or set it to the prior or next state
                prevNS = getPrevNodeState(self, self._currentTime, n)
                nextNS = getNextNodeState(self, self._currentTime, n)

                if prevNS is None and nextNS is not None:
                    pos = nextNS.getPosition()
                    n.setLocation(pos[0], pos[1])
                elif prevNS is not None and nextNS is None:
                    pos = prevNS.getPosition()
                    n.setLocation(pos[0], pos[1])
                elif prevNS is not None and nextNS is not None:
                    # interpolate
                    fraction = (self.getCurrentTime() - prevNS.getFrame().getTime()) / (nextNS.getFrame().getTime() - prevNS.getFrame().getTime())
                    pos = getInterpolatedPos(prevNS.getPosition(), nextNS.getPosition(), fraction)
                    n.setLocation(pos[0], pos[1])

        for t in self._tracks:
            clips = t.getClips()

            activeClip = False
            for c in clips:
                if (self._currentTime >= c.getStartTime()) and (self._currentTime <= (c.getStartTime() + c.getTotalDuration())):
                    intensity = c.getIntensity(self._currentTime - c.getStartTime())
                    t.getSMA().setTension(intensity)
                    activeClip = True

            if not activeClip:
                t.getSMA().setTension(0)

    def getClipAtTime(self, time, track, notClip=None):
        clips = track.getClips()
        for c in clips:
            if c is not notClip:
                if (time >= c.getStartTime()) and (time <= (c.getStartTime() + c.getTotalDuration())):
                    return c

        return None

    def getTimeAtPos(self, x):
        return x / self._timelineview.getCanvas().winfo_width() * self._maxTime

    def togglePlayPause(self):
        if self._stop:
            self.play()
        else:
            self.pause()

        return not self._stop

    def resetSimulation(self):
        nodes = self._getAllNodes()
        self.prepareSkinMesh()
        self.assignSkinNodesToSMANodes()
        for n in nodes:
            n.setMovable(True)
            n.resetSimulation()

        self._skinLayer.resetSimulation()

    def play(self):
        global globalvars
        globalvars.simulationRunning = True
        self.resetAnimationHasRun()

        self.setSceneTime(0)
        self._resetTime = False
        self._count = 0


        if self._stop:
            self.resetSimulation()
            self._window.after(0, self._playing)
            self._startTime = time.time() * 1000 - self._currentTime

        self._stop = False

        # find new max clip time
        self._maxClipTime = 0
        clips = self.getClips()

        for c in clips:
            clipEndTime = c.getStartTime() + c.getTotalDuration()
            if clipEndTime > self._maxClipTime:
                self._maxClipTime = clipEndTime

    def pause(self):
        global globalvars
        globalvars.simulationRunning = False
        if self._stop == False:
            self._stop = True

            nodes = self._getAllNodes()
            for n in nodes:
                n.resetToOriginLocation()

            self._skinLayer.resetAllPositions()

        self._controller.allPowerOff()
        clips = self.getClips()
        for c in clips:
            c.setActuatingOn(False)

    def stop(self):
        global globalvars
        globalvars.simulationRunning = False
        if self._stop == False:
            self._stop = True
            self._resetTime = True

            nodes = self._getAllNodes()
            for n in nodes:
                n.resetToOriginLocation()

            self._skinLayer.resetAllPositions()

        self.setSceneTime(0)

        self._controller.allPowerOff()
        clips = self.getClips()
        for c in clips:
            c.setActuatingOn(False)

        self.clearOldSkinMesh()
        self.updateAllViews()

    def isPlaying(self):
        return not self._stop

    def getCurrentFrame(self):
        return self._currentFrame

    def getCurrentTime(self):
        return self._currentTime

    def _saveNodeState(self, scene, node):
        currentFrame = scene.getCurrentFrame()

        if currentFrame is None:
            currentFrame = AMFrame(scene.getCurrentTime())
            scene.addFrame(currentFrame)

        state = AMNodeState(node, node.getLocation())
        currentFrame.setNodeState(state)
        self.setCurrentFrame(currentFrame)

    def setCurrentFrame(self, frame):
        self._currentFrame = frame


    def setMaxTime(self, maxtime):
        self._maxTime = maxtime

    def getMaxTime(self):
        return self._maxTime

    def deleteCurrentFrame(self):
        if self._currentFrame is not None:
            self.removeFrame(self._currentFrame)
            self._currentFrame = None

        self.updateAllViews()

    def nextFrame(self):
        frame = getNextFrame(self, time=self._currentTime)

        if frame is not None:
            self.jumpToFrame(frame)

        self.updateAllViews()

    def previousFrame(self):
        frame = getPreviousFrame(self, time=self._currentTime)

        if frame is not None:
            self.jumpToFrame(frame)

        self.updateAllViews()

    def updateAllViews(self):
        if self._mainview is not None:
            self._mainview.updateView()

        if self._timelineview is not None:
            self._timelineview.updateView()

    def getRecordedNodes(self):
        return self._recordedNodes

    def resetAnimationHasRun(self):
        self._animationRanWithError = False
        self._animHasRun = False

    def _checkIfAnimationHasRun(self):
        self._maxClipTime

        if not self._stop and self._currentTime > self._maxClipTime:
            self._animHasRun = True

        if self._mainview.foundError():
            self._animationRanWithError = True

    def hasAnimationRunWithError(self):
        return self._animationRanWithError

    def animationHasRun(self):
        if len(self.getClips()) == 0:
            self._mainview.updateView()
            self._animationRanWithError = False
            if self._mainview.foundError():
                self._animationRanWithError = True
            return True

        return self._animHasRun

    def removeClipsForSMA(self, sma):
        track = self.getTrackFor(sma)
        clips = track.getClips()

        for c in clips:
            track.removeClip(c)
