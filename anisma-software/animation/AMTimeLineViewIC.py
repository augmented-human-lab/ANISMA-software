from UIElements.Button import *
from animation.AMUtilities import *
from animation.AMFactory import *
from components.SMANode import SMANode
from animation.AMClip import AMClip
import time, sys
import controller.Controller
import threading
import tkinter.messagebox

class AMTimeLineViewIC():

    def _checkForDevice(self):
        if (self._controller.newDeviceDetected()):
                anismaPort = self._controller.findANISMAControllerDevice()
                self._controller.connect(anismaPort)

        if (self._controller.isConnected() is not self._lastConnected):
            if (not self._controller.isConnected()):
                self._serialcbval.set(0)
                self._serialcb.configure(state='disabled')
                self.cb_contract_click()
            else:
                # self._serialcb.set(1) 
                self._serialcb.configure(state='normal')

        self._lastConnected = self._controller.isConnected()
        t = threading.Timer(2.0, self._checkForDevice)
        t.daemon = True
        t.start()
        
    def __init__(self, window, canvas, timeLineView, scene, mainView, controller):
        self.__window = window
        self._canvas = canvas
        self._timeLineView = timeLineView
        self._scene = scene
        self._mainView = mainView
        self._controller = controller
        self._draggingClipOffset = 0
        self._draggingClip = None
        self._clickTime = 0
        self._dragstartposx = 0

        self._popup = None

        self.__mousePoint = [0,0]
        self.__hoveredObject = None
        
        if sys.platform.startswith('darwin'):
           self._canvas.bind("<ButtonPress-2>", self.onRightMousePressedOnView)
        else:
            self._canvas.bind("<ButtonPress-3>", self.onRightMousePressedOnView)

        self._canvas.bind("<ButtonPress-1>", self.onMousePressedOnView)
        self._canvas.bind("<ButtonRelease-1>", self.onMouseReleasedOnView)
        self._canvas.bind("<Motion>", self.onMouseMovedOnView)
        self._canvas.bind("<B1-Motion>", self.onMouseDragOnView)
        self._canvas.bind("<Enter>", self.onMouseEnter)
        self._canvas.bind("<Leave>", self.onMouseLeave)

        self.__window.bind("<BackSpace>", self.onPressBackSpace)
        self.__window.bind("<Left>", self.onPressArrowLeft)
        self.__window.bind("<Right>", self.onPressArrowRight)

        self.__window.bind("<space>", self.onPressSpace)
        self._canvas.bind("<MouseWheel>", self.onScroll)

        self._serialcbval = BooleanVar()
        self._serialcb = None
        self._lastReleaseTime = 0
        
        if controller.isConnected():
            self._serialcb = Checkbutton(self._canvas, text="Replay with Controllerboard", anchor=CENTER,background="#DFE6EE", variable=self._serialcbval, command=self.cb_contract_click, onvalue = True, offvalue = False)
        else:
            self._serialcb = Checkbutton(self._canvas, text="Replay with Controllerboard", anchor=CENTER,background="#DFE6EE", state=DISABLED, variable=self._serialcbval, command=self.cb_contract_click, onvalue = True, offvalue = False)
        self._lastConnected = self._controller.isConnected()

        self._serialcb.place(x=self._canvas.winfo_width()-200, y=24/2)
        self._timeLineView.setControllerActiveCB(self._serialcb)

        t = threading.Timer(2.0, self._checkForDevice)
        t.daemon = True
        t.start()

    def cb_contract_click(self):
        run_through_simulation = self._scene.animationHasRun()
        errors_detected = self._scene.hasAnimationRunWithError()
        do_setactive = False
        active = self._serialcbval.get()
        if active:
            if not run_through_simulation:
                MsgBox = messagebox.askquestion('Warning: Simulation Not Run', 'It is recommended to run the simulation at least once after making any changes.\n\n(This helps to detect potential problems before the physical actuation.)\n\nDo you still wish to continue to activate the controller board?', icon = 'warning')
                if MsgBox == 'yes':
                    do_setactive = True
            else:
                if errors_detected:
                    MsgBox = messagebox.askquestion('Warning: Design Issue Detected', "It is recommended to fix any potential design issues before actuating the physical device.\n\nDo you still wish to continue to activate the controller board?", icon = 'warning')
                    if MsgBox == 'yes':
                        do_setactive = True
                else:
                    do_setactive = True


        if not active or (active and do_setactive):
            nodes = []
            # prepare export
            objs = self._mainView.getAllObjects()
            for o in objs:
                if isinstance(o, SMANode):
                    o.displayPin(active)

            self._mainView.setControllerBoardActive(active)
            self._timeLineView.setControllerBoardActive(active)
            self._scene.setControllerBoardActive(active)
            self._timeLineView.updateView()
            self._mainView.updateView()
        else:
            self._serialcbval.set(False)

    def getControllerCheckBox(self):
        return self._serialcb

    def onScroll(self, event):
        self._timeLineView.scrollTracks(event.delta)
        self._timeLineView.updateView()

    def onMouseMovedOnView(self, event=None):
        self.__mousePoint = [event.x,event.y]

        self._updateAMViewCursor(self.__mousePoint.copy(),stickCloseFrame=True)

        ## Highlight hovered component
        # un highlight last
        if self.__hoveredObject is not None:
            self.__hoveredObject.isHighlighted = False

        # find closest component
        obj = self._timeLineView.findClosest(self.__mousePoint)

        # if found one highlight it
        if obj is not None:
            obj.isHighlighted = True
        else:
            self.__window.config(cursor="")

            if self.__mousePoint[0] > self._timeLineView.getTimeLineInlet():
                hoverClip = self._timeLineView.getHoveredClip()

                if hoverClip is not None:
                    if sys.platform.startswith('darwin'):
                        self.__window.config(cursor="hand")
                    else: 
                        self.__window.config(cursor="hand1")

        self.__hoveredObject = obj

        self._timeLineView.updateView()
        self._mainView.updateView()

    def _getCloseFrameTime(self, x):
        width = self._timeLineView.getTimeLineWidth()
        x = min(width, max(self._timeLineView.getTimeLineInlet(), x))
        newTime = int(x / width * self._scene.getMaxTime())
        frame = getFrameBetween(self._scene, newTime - 200, newTime + 200)

        if frame is not None:
            return frame.getTime()
        else:
            return None

    def _updateAMViewCursor(self, pos, stickCloseFrame=False):
        if stickCloseFrame:
            width = self._timeLineView.getTimeLineWidth()-self._timeLineView.getRightTimeInlet()
            x = min(width, max(self._timeLineView.getTimeLineInlet(), pos[0]))

            newTime = int(x / width * self._scene.getMaxTime())
            newTime = self._getCloseFrameTime(x)

            if newTime is not None:
                self._timeLineView.setCursorPos([newTime / self._scene.getMaxTime() * width, pos[1]])
            else:
                self._timeLineView.setCursorPos(pos)
        else:
            self._timeLineView.setCursorPos(pos)

    def _setNewSliderPos(self, x):
        width = self._timeLineView.getTimeLineWidth()-self._timeLineView.getRightTimeInlet()
        x = min(width, max(0, x-self._timeLineView.getTimeLineInlet()))

        newTime = int(x / width * self._scene.getMaxTime())
        newTimeN = self._getCloseFrameTime(x)

        if newTimeN is not None:
            newTime = newTimeN

        self._scene.setSceneTime(newTime)
        self._mainView.updateView()

        self._timeLineView.updateView()

    def onMousePressedOnView(self, event=None):
        self._clickTime = time.time() * 1000
        if event.x > self._timeLineView.getTimeLineInlet():
            self._draggingClip = self._timeLineView.getHoveredClip()
        else:
            self._draggingClip = None

        if isinstance(self.__hoveredObject, Button):
            self.__hoveredObject.onClick()
        elif self._draggingClip is not None:
            self._draggingClipOffset = self._draggingClip.getStartTime() - self._scene.getTimeAtPos(event.x-self._timeLineView.getTimeLineInlet())
            self._dragstartposx = event.x
        else:
            self._setNewSliderPos(event.x)
            if self._scene.isPlaying(): # continue playing from new set time
                self._scene.play()

    def onRightMousePressedOnView(self, event=None):
        clip = self._timeLineView.getHoveredClip()
        if clip is not None:
            self._scene.removeClip(clip)
            self._scene.updateAllViews()

    def onMouseReleasedOnView(self, event=None):
        if self._draggingClip is not None and (time.time() * 1000 - self._clickTime) < 500:
            if self._popup is not None and not self._popup.isHidden():
                self._popup.remove()

            if abs(self._dragstartposx - event.x) < 5 and self._popup:
                self._popup = createAMSMAPopUp(self._draggingClip.getTrack().getSMA(), self._mainView, [200, 200], self._scene, clip=self._draggingClip)
            self._mainView.updateView()

        newReleaseTime = time.time()
        print(newReleaseTime - self._lastReleaseTime)
        if newReleaseTime - self._lastReleaseTime <= 0.2:
            # doubleclick
            tracks = self._scene.getTracks()
            highlightedTrack = None
            for t in tracks:
                if t.isHighlighted():
                    highlightedTrack = t

            if highlightedTrack is not None:
                if self._popup is not None and not self._popup.isHidden():
                    self._popup.remove()
                self._popup = createAMSMAPopUp(highlightedTrack.getSMA(), self._mainView, [200, 200], self._scene)
                self._mainView.updateView()

        self._lastReleaseTime = newReleaseTime

    def onMouseDragOnView(self, event=None):
        self.__mousePoint = [event.x,event.y]
        self._updateAMViewCursor(self.__mousePoint)

        if self._draggingClip is not None:
            newtime = min(max(0, self._scene.getTimeAtPos(event.x-self._timeLineView.getTimeLineInlet()) + self._draggingClipOffset), self._scene.getMaxTime()-self._draggingClip.getTotalDuration())
            track = self._draggingClip.getTrack()
            clipAfter = self._scene.getClipAtTime(newtime, track, notClip=self._draggingClip)
            clipBefore = self._scene.getClipAtTime(newtime+self._draggingClip.getTotalDuration(), track, notClip=self._draggingClip)

            # Set it after a clip if the start time is on a clip
            if clipAfter is not None:
                newtime = clipAfter.getStartTime() + clipAfter.getTotalDuration()

            # Set before a colliding clip
            if clipBefore is not None:
                newtime = clipBefore.getStartTime() - self._draggingClip.getTotalDuration()

            self._draggingClip.setStartTime(newtime)
            self._timeLineView.updateView()
        else:
            self._setNewSliderPos(event.x)
            if self._scene.isPlaying(): # continue playing from new set time
                self._scene.play()


    def onMouseEnter(self, event=None):
        self._timeLineView.displayCursor(True)
        self._timeLineView.updateView()

    def onMouseLeave(self, event=None):
        self._timeLineView.displayCursor(False)
        self._timeLineView.updateView()

    def onPressBackSpace(self, event=None):
        self._scene.deleteCurrentFrame()

    def onPressSpace(self, event=None):
        self._scene.togglePlayPause()

    def onPressArrowLeft(self, event=None):
        self._scene.previousFrame()

    def onPressArrowRight(self, event=None):
        self._scene.nextFrame()
