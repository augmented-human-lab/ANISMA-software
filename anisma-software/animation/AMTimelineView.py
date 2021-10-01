from tkinter import *
from render.UIView import UIView
from UIElements.Button import Button

class AMTimelineView(UIView):
    __windowWidth = 0
    __windowHeight = 0
    _font = ("Verdana", 16)
    _displayCursor = True
    _cursorPos = [0,0]

    def __init__(self, canvas, scene):
        super().__init__(canvas)

        self._show = True

        self._canvas = canvas
        self._scene = scene

        self._startIndex = 0
        self._numberOfTracks = 6

        canvas.config(background="#FFFFFF")
        self._leftinlet = 136
        self._topinlet = 41+24
        self._rightTimeInlet = 20
        self._controllerBoardActive = False

        def cb_play(btn, animationScene):
            result = animationScene.togglePlayPause()

            if not result:
                btn.setText("Play")
            else:
                btn.setText("Pause")

        self._btn_play = Button(self._canvas, [self._canvas.winfo_width() + 100-50, 24/2+7], 50, 24, "Play", callback=cb_play, ic=scene)

        def cb_stop(btn, animationScene):
            animationScene.stop()
            self._btn_play.setText("Play")

        self._btn_stop = Button(self._canvas, [self._canvas.winfo_width() + 150-50, 24/2+7], 50, 24, "Stop", callback=cb_stop, ic=scene)
        self.add(self._btn_play)
        self.add(self._btn_stop)

    def setControllerActiveCB(self, element):
        self._serialcb = element

    def setControllerBoardActive(self, enabled):
        self._controllerBoardActive = enabled

    def getRightTimeInlet(self):
        return self._rightTimeInlet

    def getTopInlet(self):
        return self._topinlet

    def scrollTracks(self, step):
        tracks = self._scene.getTracks()
        self._startIndex += step
        self._startIndex = max(0, min(len(tracks) - self._numberOfTracks, self._startIndex))

    def _getFormattedTime(self, time, nomillis=False):
        millis = (time) % 1000
        millis = int(millis)

        secs=(time/1000)%60
        secs = int(secs)
        mins=(time/(1000*60))%60
        mins = int(mins)
        if nomillis:
            return ("{:02}:{:02}".format(mins, secs))
        else:
            return ("{:02}:{:02}:{:03}".format(mins, secs, millis))

    def _drawFrames(self):
        color = "orange"
        size = [self.getTimeLineWidth()-self._rightTimeInlet, self._canvas.winfo_height()]

        trisize = 6/2
        width = 2

        for f in self._scene.getFrames():
            fraction = f.getTime() / self._scene.getMaxTime()
            id = self._canvas.create_polygon(self._leftinlet+size[0]*fraction-trisize, size[1], self._leftinlet+size[0]*fraction+trisize, size[1], self._leftinlet+size[0]*fraction, size[1]-trisize, fill=color, outline=color, width = 2)
            self._canvas.lower(id)
            id = self._canvas.create_polygon(self._leftinlet+size[0]*fraction-trisize, self._topinlet, self._leftinlet+size[0]*fraction+trisize, self._topinlet, self._leftinlet+size[0]*fraction, trisize+self._topinlet, fill=color, outline=color, width = 2)
            self._canvas.lower(id)

    def getTimeLineWidth(self):
        return self._canvas.winfo_width() - self._leftinlet

    def getTimeLineInlet(self):
        return self._leftinlet

    def getHoveredClip(self):
        tracks = self._scene.getTracks()
        size = [self.getTimeLineWidth(), self._canvas.winfo_height() - self._topinlet]
        padding = 1

        clipHeight = (size[1] - self._numberOfTracks*(padding+1)) / self._numberOfTracks

        yLocation = padding + self._topinlet

        for i in range(self._startIndex, min(self._startIndex+self._numberOfTracks, len(tracks))):
            clips = tracks[i].getClips()

            for c in clips:
                x0 = self._leftinlet+(c.getStartTime() / self._scene.getMaxTime()) * (size[0]-self._rightTimeInlet)
                x1 = self._leftinlet+((c.getStartTime() + c.getTotalDuration()) / self._scene.getMaxTime()) * (size[0]-self._rightTimeInlet)

                if self._cursorPos[0] >= x0 and self._cursorPos[0] <= x1 and self._cursorPos[1] >= yLocation and self._cursorPos[1] <= yLocation + clipHeight:
                    return c

            yLocation += clipHeight + padding

        return None

    def markHighlightedTracks(self):
        tracks = self._scene.getTracks()
        size = [self._canvas.winfo_width(), self._canvas.winfo_height()-self._topinlet]
        padding = 1
        clipHeight = (size[1] - self._numberOfTracks*(padding+1)) / self._numberOfTracks
        yLocation = padding + self._topinlet

        for i in range(self._startIndex, min(self._startIndex+self._numberOfTracks, len(tracks))):
            tracks[i].getSMA().isHighlighted = False
            tracks[i].setHighlighted(False)

            if self._cursorPos[0] >= self._leftinlet and self._cursorPos[0] <= size[0]-self._leftinlet-self._rightTimeInlet and self._cursorPos[1] >= yLocation and self._cursorPos[1] <= yLocation + clipHeight:
                tracks[i].setHighlighted(True)
                tracks[i].getSMA().isHighlighted = True

            yLocation += clipHeight + padding


    def _drawTracks(self):
        tracks = self._scene.getTracks()
        size = [self._canvas.winfo_width(), self._canvas.winfo_height()-self._topinlet]
        padding = 1

        clipHeight = (size[1] - self._numberOfTracks*(padding+1)) / self._numberOfTracks

        yLocation = padding + self._topinlet

        for i in range(self._startIndex, min(self._startIndex+self._numberOfTracks, len(tracks))):
            clips = tracks[i].getClips()

            highlight_track = tracks[i].isHighlighted()

            if highlight_track:
                self._canvas.create_rectangle(0, yLocation, self._canvas.winfo_width(), yLocation+clipHeight, fill="#EFF6FE", outline="", width=2)#, tags="nonpersist"
            else:
                self._canvas.create_rectangle(0, yLocation, self._canvas.winfo_width(), yLocation+clipHeight, fill="#DFE6EE", outline="", width=2)#, tags="nonpersist"

            self._canvas.create_text(self._leftinlet / 2, yLocation + clipHeight/2, anchor=CENTER, font=self._font, text=tracks[i].getSMA().getName() + " (" + str(tracks[i].getSMA().getContractionFraction()) + "%)", fill="#12333D")

            for c in clips:
                x0 = self._leftinlet+(c.getStartTime() / self._scene.getMaxTime()) * (size[0]-self._leftinlet-self._rightTimeInlet)
                x1 = self._leftinlet+((c.getStartTime() + c.getTotalDuration()) / self._scene.getMaxTime()) * (size[0]-self._leftinlet-self._rightTimeInlet)
                color_fill = '#C6D0DD'
                color_outline = '#CCCCCC'

                if self._cursorPos[0] >= x0 and self._cursorPos[0] <= x1 and self._cursorPos[1] >= yLocation and self._cursorPos[1] <= yLocation + clipHeight:
                    color_fill = '#D6E0ED'
                    color_outline = '#AAAAAA'

                self._canvas.create_rectangle(x0, yLocation, x1, yLocation+clipHeight, fill=color_fill, outline=color_outline, width=0)#, tags="nonpersist"

                path = c.getDrawingPath()
                adjustedPath = []
                intend = 2
                for l in path:
                    cWidth = (x1-x0) - intend*2
                    adjustedPath.append([x0 + intend + l[0] * cWidth, yLocation - intend + clipHeight - l[1] * (clipHeight-intend*2)])
                self._canvas.create_line(adjustedPath, width=3, joinstyle=ROUND, capstyle=ROUND, fill='#9473FF')#, tags="nonpersist")

            yLocation += clipHeight + padding

    def setCursorPos(self, pos):
        self._cursorPos = pos
        self._cursorPos[0] = max(self._leftinlet, min(self._cursorPos[0], self._canvas.winfo_width()))
        self._cursorPos[1] = max(self._topinlet, min(self._cursorPos[1], self._canvas.winfo_height()))
        self.markHighlightedTracks()

    def displayCursor(self, enabled):
        self._displayCursor = enabled

    def show(self, enabled):
        self._show = enabled
        if enabled:
            self._canvas.pack(side=BOTTOM, fill=X, expand=0)
        else:
            self._canvas.pack_forget()

    def updateView(self):

        if self._show:

            self._serialcb.place(x=self._canvas.winfo_width()-200, y=24/2)
            self._btn_play.setLocation(self._canvas.winfo_width()/2 + 200-70, 24/2+7)
            self._btn_stop.setLocation(self._canvas.winfo_width()/2 + 255-70, 24/2+7)
            self._canvas.delete("all")

            size = [self._canvas.winfo_width(), self._canvas.winfo_height()]

            # draw timeline time steps
            pID = self._canvas.create_rectangle(0, self._topinlet, size[0], self._topinlet-24, fill="#B0BAC5", outline="")
            timestep = 10000
            ticksize = 5
            maxtime = self._scene.getMaxTime()
            steps = int(maxtime / timestep) + 1
            for i in range(steps):
                #get postion
                ticktime = i * timestep
                timestr = self._getFormattedTime(ticktime, nomillis=True)
                tickpos = self._leftinlet + ticktime / self._scene.getMaxTime() * (size[0]-self._leftinlet-self._rightTimeInlet)

                # draw line
                self._canvas.create_line(tickpos, self._topinlet, tickpos, self._topinlet-ticksize, width=1, joinstyle=ROUND, capstyle=ROUND, fill="#667587")

                # draw time text
                self._canvas.create_text(tickpos, self._topinlet-24/2, anchor=CENTER, font=("Verdana", 10), text=timestr, fill="#12333D")

            pID = self._canvas.create_rectangle(0, 0, size[0], self._topinlet-24, fill="#DFE6EE", outline="")

            # draw seperator lines
            pID = self._canvas.create_rectangle(0, self._topinlet, self._leftinlet, size[1], fill="#EDEFF3", outline="")
            self._canvas.lower(pID)
            self._canvas.create_line(0, self._topinlet, size[0], self._topinlet, width=1, joinstyle=ROUND, capstyle=ROUND, fill="#8091A5")
            self._canvas.create_line(0, 1, size[0], 1, width=1, joinstyle=ROUND, capstyle=ROUND, fill="#8091A5")

            self._drawTracks()
            self._drawFrames()

            # print current time text
            curTimeStr = self._getFormattedTime(self._scene.getCurrentTime())
            maxTimeStr = self._getFormattedTime(self._scene.getMaxTime())
            self._canvas.create_text(size[0]/2, 24/2+7, anchor=CENTER, font=self._font, text=(curTimeStr + " / " + maxTimeStr), fill="#12333D")

            if self._displayCursor:
                self._canvas.create_line(self._cursorPos[0], self._topinlet, self._cursorPos[0], size[1], width=1, joinstyle=ROUND, capstyle=ROUND, fill="#12333D")

            self._canvas.create_line(self._leftinlet, self._topinlet, self._leftinlet, size[1], width=1, joinstyle=ROUND, capstyle=ROUND, fill="#8091A5")

            if self._controllerBoardActive:
                pID = self._canvas.create_rectangle(0, 0, size[0], 5, fill="#FF006E", outline="")

            super().updateView(noDelete=True)
