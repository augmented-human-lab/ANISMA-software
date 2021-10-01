from tkinter import *
from render.RenderingObject import *
from simulation.Model import *
from animation.AMClip import *
from util.drawUtil import *

class AMSMAPopUp(RenderingObject):
    _title_height = 25
    _hoveredButton = -1
    __updateCount = 0

    def __init__(self, view, location, width, title, scene, smaConnection, clip=None):
        self._parent = view.getCanvas()
        self._view = view
        self._location = location
        self._smaConnection = smaConnection
        self._scene = scene
        self._clip = clip
        self._duration = 0

        self._height = 190+15
        self._width = width
        self._menuCanvas = Canvas(self._parent, width=width, height=self._height, bd=0, highlightthickness=0)

        self._title = title
        self._normalFont = ("Verdana", 13)

        self._menuCanvas.bind("<Motion>", self.onMouseMoved)
        self._menuCanvas.bind("<B1-Motion>", self.onMouseDrag)
        self._menuCanvas.bind("<ButtonPress-1>", self.onMousePressed)
        self._menuCanvas.bind("<Enter>", self.onMouseEnter)
        self._menuCanvas.bind("<Leave>", self.onMouseLeave)

        self._hidden = False
        self._buttons = []

        self._menuCanvas.pack()


        tf_width = 52
        self._titlebar_height = 40
        self._startTimeStr = StringVar()
        self.tf_starttime = Entry(self._menuCanvas, textvariable=self._startTimeStr)

        if clip is not None:
            self.tf_starttime.insert(END, str(int(clip.getStartTime())))
        else:
            self.tf_starttime.insert(END, scene.getCurrentTime())

        self._powerStr = StringVar()
        self.tf_power = Entry(self._menuCanvas, textvariable=self._powerStr)
        self._powerStr.trace("w", self._onChangedPower)
        if clip is not None:
            self.tf_power.insert(END, str(int(clip.getPower()*100)))
        else:
            self.tf_power.insert(END, "75")


        self._durationStr = StringVar()
        self.tf_duration = Entry(self._menuCanvas, textvariable=self._durationStr)
        self._durationStr.trace("w", self._onChangedDuration)
        if clip is not None:
            self.tf_duration.insert(END, str(int(clip.getActuationDuration())))
        else:
            self.tf_duration.insert(END, str(min(self._getMaxActuationDuration(self._smaConnection,self._tension*100), 2000)))

        self._menuCanvas.create_window(20+160+60+tf_width/2, self._titlebar_height+15, width=tf_width, height=25, window=self.tf_starttime)
        self._menuCanvas.create_window(20+160+60+tf_width/2, self._titlebar_height+15+25*2, width=tf_width, height=25, window=self.tf_power)
        self._menuCanvas.create_window(20+160+60+tf_width/2, self._titlebar_height+15+25, width=tf_width, height=25, window=self.tf_duration)

        if clip is not None:
            Button(self._menuCanvas, text="save", command=self._onAddActuationBehavior, width=7, height=1).place(x=215+25-10, y=110+15+50-5)
            Button(self._menuCanvas, text="delete", command=self._onRemoveActuationBehavior, width=7, height=1).place(x=215+25-10-75, y=110+15+50-5)
            Button(self._menuCanvas, text="cancel", command=self.remove, width=7, height=1).place(x=215-200+10, y=110+15+50-5)
        else:
            Button(self._menuCanvas, text="add", command=self._onAddActuationBehavior, width=7, height=1).place(x=215+25-10, y=110+15+50-5)
            Button(self._menuCanvas, text="cancel", command=self.remove, width=7, height=1).place(x=215-200+10, y=110+15+50-5)


    def _onAddActuationBehavior(self):
        clip = self._clip

        if clip is not None:
            clip.setStartTime(min(self._scene.getMaxTime(), max(0, int(self._startTimeStr.get()))))
            clip.setPower(self._tension)
            clip.setActuationDuration(self._duration)
        else:
            clip = AMClip(min(self._scene.getMaxTime(), max(0, int(self._startTimeStr.get()))), self._tension, self._duration, self._smaConnection)
            self._scene.addClip(clip, self._smaConnection)

        self.remove()
        self._scene.updateAllViews()


    def _onRemoveActuationBehavior(self):

        self._scene.removeClip(self._clip)

        self.remove()
        self._scene.updateAllViews()


    def isInBounds(self, x, y):
        return False

    def update(self, zoomlevel):
        if not self._hidden:
            self._menuCanvas.delete("nonpersist")

            title_height = 25

            bold_font = ("Verdana", 12, "bold")
            self._menuCanvas.create_rectangle(0, 0, self._width-1, self._height-1, fill='#F3F5F9', outline='#CCCCCC', width=1, tags="nonpersist")
            self._menuCanvas.create_rectangle(0, 0, self._width-1, title_height, fill='#12333D', outline='#CCCCCC', width=1, tags="nonpersist")
            self._menuCanvas.create_text(self._width/2.0-3.8*len(self._title), title_height/2.0, anchor=W, font=bold_font, text=self._title, tags="nonpersist", fill="#FFFFFF")

            # textbox labels
            self._menuCanvas.create_text(20+160, self._titlebar_height + 15, anchor=W, font=self._normalFont, text="start time", tags="nonpersist")
            self._menuCanvas.create_text(20+160+60+55, self._titlebar_height + 15, anchor=W, font=self._normalFont, text="ms", tags="nonpersist")

            self._menuCanvas.create_text(20+160, self._titlebar_height + 15 + 25*2, anchor=W, font=self._normalFont, text="at power", tags="nonpersist")
            self._menuCanvas.create_text(20+160+60+55, self._titlebar_height + 15 + 25*2, anchor=W, font=self._normalFont, text="%", tags="nonpersist")

            self._menuCanvas.create_text(20+160, self._titlebar_height + 15 + 25, anchor=W, font=self._normalFont, text="contract", tags="nonpersist")
            self._menuCanvas.create_text(20+160+60+55, self._titlebar_height + 15 + 25, anchor=W, font=self._normalFont, text="ms", tags="nonpersist")

            # draw graphical signal
            self._drawGraph()

            # place popup at set mouse pos location
            self._menuCanvas.place(x=self._location[0], y=self._location[1], height=self._height)

    def _drawValidHull(self):
        self._menuCanvas.create_polygon(self._validHullPoly, fill="#FFFFFF")

    def _getValidHullPoly(self):
        minx = 20
        maxx = 150 + 20
        miny = self._titlebar_height + 5
        maxy = self._titlebar_height + 65

        maxtime = 20000
        maxforce = getUpperForceLimit(getMaxPower(self._smaConnection.getSMAParameters()), self._smaConnection.getSMAParameters())

        validHull = self._getValidHull()
        processedHull = []

        for p in validHull:
            x = minx + (p[0] / maxtime) * (maxx-minx)
            y = miny + (1 - (p[1] / maxforce)) * (maxy - miny)
            processedHull.append([x,y])

        return processedHull

    def _drawGraph(self):
        #draw backgorund
        width = 150
        height = 65
        intend = 20
        self._menuCanvas.create_rectangle(intend, self._titlebar_height, width+intend, self._titlebar_height+height+10, fill='#DFE6EE', outline='#CCCCCC', width=1, tags="nonpersist")

        # axis titles
        self._menuCanvas.create_text(10, 93+15, anchor=W, font=("Verdana", 10), text="intensity (%)", tags="nonpersist", angle=90)
        self._menuCanvas.create_text(intend+width/2, 110+15, anchor=CENTER, font=("Verdana", 10), text="time (s)", tags="nonpersist")
        self._menuCanvas.create_text(intend, 110+15, anchor=CENTER, font=("Verdana", 10), text="0", tags="nonpersist")
        self._menuCanvas.create_text(intend+width, 110+15, anchor=CENTER, font=("Verdana", 10), text="20", tags="nonpersist")

        # draw signal
        maxIntensity = getUpperForceLimit(getMaxPower(self._smaConnection.getSMAParameters()), self._smaConnection.getSMAParameters())
        power = getMinPower() + self._tension * (getMaxPower(self._smaConnection.getSMAParameters()) - getMinPower())

        maxTime = 20000
        duration = self._duration

        step = 100
        prevPoint = [intend, self._titlebar_height + height + 5]
        points = []
        points.append(prevPoint)

        # create rising signal
        force = 0
        for i in range(int(duration/step)):
            time = i * step
            force = getForce(time, power, self._smaConnection.getSMAParameters())
            y = min(self._titlebar_height + height + 5, self._titlebar_height + height + 5 - height*force/maxIntensity)
            nextPoint = [intend+time*width/maxTime, y]
            points.append(nextPoint)

        # create falling signal
        for i in range(int((maxTime-duration)/step)):
            time = i * step
            force = getRelaxForce(time, duration, power, self._smaConnection.getSMAParameters())
            y = min(self._titlebar_height + height + 5, self._titlebar_height + height + 5 - height*force/maxIntensity)
            x = intend+(duration + time)*width/(maxTime)
            nextPoint = [x, y]
            points.append(nextPoint)

        # display calculated attack, sustain, release time
        attackTime = min(getAttackTime(power, self._smaConnection.getSMAParameters()), self._duration)
        sustainTime = max(self._duration - attackTime, 0)
        releaseTime = getRelaxTime(5, duration, power, self._smaConnection.getSMAParameters())
        self._menuCanvas.create_text(intend+60+100, 170+15-40, anchor=W, font=("Verdana", 12), text="relax time:", tags="nonpersist")
        self._menuCanvas.create_text(width+intend+100-20-40+90, 170+15-40, anchor=E, font=("Verdana", 12), text=str(int(releaseTime))+"ms", tags="nonpersist")

        # draw dashed indicator lines
        y0 = min(self._titlebar_height + height + 5, self._titlebar_height + height + 5 - height*0.0)+5
        y1 = min(self._titlebar_height + height + 5, self._titlebar_height + height + 5 - height*1.0)-5
        x = intend+(attackTime)*width/(maxTime)
        location = [x, y]

        x = intend+(attackTime+sustainTime)*width/(maxTime)
        location = [x, y]
        color = 'black'
        if self._duration == self._getMaxActuationDuration(self._smaConnection,self._tension*100):
            color = 'red'
        self._menuCanvas.create_line(x, y0, x, y1, width=1, joinstyle=ROUND, capstyle=ROUND, fill=color, tags="nonpersist")#, dash=(5,))
        x0 = intend
        x1 = intend+width
        y  = min(self._titlebar_height + height + 5, self._titlebar_height + height + 5 - height*getRelaxForce(0, duration, power, self._smaConnection.getSMAParameters())/maxIntensity)
        location = [x, y]
        self._menuCanvas.create_line(x0, y, x1, y, width=1, joinstyle=ROUND, capstyle=ROUND, fill='black', tags="nonpersist")

        x = intend+width*min(1,(attackTime+sustainTime+releaseTime)/(maxTime))
        location = [x, y]
        self._menuCanvas.create_line(x, y0, x, y1, width=1, joinstyle=ROUND, capstyle=ROUND, fill='gray', tags="nonpersist", dash=(5,))

        # finally draw actual signal on top
        self._menuCanvas.create_line(points, width=4, joinstyle=ROUND, capstyle=ROUND, fill='#9473FF', tags="nonpersist")

        # draw point of interest (duration, intensity)
        y = min(self._titlebar_height + height + 5, self._titlebar_height + height + 5 - height*getRelaxForce(0, duration, power, self._smaConnection.getSMAParameters())/maxIntensity)
        x = intend+(duration)*width/(maxTime)
        location = [x, y]
        size = 3
        self._menuCanvas.create_oval(location[0]-size, location[1]-size, location[0]+size, location[1]+size, fill="white", outline="black", width=1)

    def addButton(self, button):
        self._buttons.append(button)

    def getCanvas(self):
        return self._menuCanvas

    def onMouseMoved(self, event=None):
        self.update(0)

    def _getMaxActuationDuration(self, sma, pwr_percent):
        smaParams = sma.getSMAParameters()

        pwr = pwr_percent
        if smaParams.getSpringDiameter() == 1.37:
            return min((32.47349 - 0.5909057*pwr + 0.002824006*pwr**2)*1000, 10000)
        elif smaParams.getSpringDiameter() == 2.54:
            return min((126.2 - 2.22*pwr + 0.01*pwr**2)*1000, 10000)
        else:
            print("ERROR: UNKNOWN SMA TYPE")
            return 0

    def _findPower(self, time, force):

        pwr = getPowerToObtainMaxForce(force, self._smaConnection.getSMAParameters())

        if getAttackTime(pwr, self._smaConnection.getSMAParameters()) <= time:
            return pwr
        else:
            pwr = getMaxPower(self._smaConnection.getSMAParameters())
            savepwr = pwr
            while pwr >= getMinPower():
                pwr -= 0.01
                if getForce(time, pwr, self._smaConnection.getSMAParameters()) >= force-10 and getForce(time, pwr, self._smaConnection.getSMAParameters()) <= force+10:
                    return pwr

            return None

    def _getValidHull(self):
        maxforce = getUpperForceLimit(getMaxPower(self._smaConnection.getSMAParameters()), self._smaConnection.getSMAParameters())

        minpower = 0
        maxpower = getMaxPower(self._smaConnection.getSMAParameters())

        minTime = 500
        maxTime = 10000

        hull = []

        for p in range(0, int(maxpower*100), 1):
            for t in range(minTime, maxTime, 500):
                maxduration = self._getMaxActuationDuration(self._smaConnection, p)
                if t <= maxduration:
                    force = getForce(t, p/100, self._smaConnection.getSMAParameters())
                    hull.append([t, force])

        hull = getConvexHullPoly(hull)

        return hull.exterior.coords

    def _setGraphPoint(self, event=None):
        # clicked in graph
        minx = 20
        maxx = 150+20
        miny = self._titlebar_height + 5
        maxy = self._titlebar_height + 65

        maxtime = 20000
        maxforce = getUpperForceLimit(getMaxPower(self._smaConnection.getSMAParameters()), self._smaConnection.getSMAParameters())
        if event.x > minx and event.x < maxx and event.y > 0 and event.y < maxy:
            time = min(self._getMaxActuationDuration(self._smaConnection, self._tension*100), ((event.x - minx) / (maxx - minx)) * maxtime)
            force = (1- max(0, (event.y - miny) / (maxy - miny))) * maxforce


            pwr = getPowerToObtainMaxForce(force, self._smaConnection.getSMAParameters())

            if getAttackTime(pwr, self._smaConnection.getSMAParameters()) <= time:
                self.setPower(pwr,isCurrentVal=True)
                self.setDuration(time)
            else:
                pwr = getMaxPower(self._smaConnection.getSMAParameters())
                savepwr = pwr
                found = False
                while pwr >= getMinPower():
                    pwr -= 0.01
                    if getForce(time, pwr, self._smaConnection.getSMAParameters()) >= force-10 and getForce(time, pwr, self._smaConnection.getSMAParameters()) <= force+10:
                        self.setPower(pwr, isCurrentVal=True)
                        self.setDuration(time)
                        found = True
                        break

                if not found:
                    print("no found")

        self._view.updateView()
        self.update(0)

    def onMousePressed(self, event=None):
        self._setGraphPoint(event)

    def onMouseDrag(self, event=None):
        self._setGraphPoint(event)

    def onMouseReleased(self, event=None):
        return

    def onMouseLeave(self, event=None):
        self._hoveredButton = -1
        self.update(0)

    def onMouseEnter(self, event=None):
        self.update(0)

    def hide(self):
        self._menuCanvas.place_forget()
        self._hidden = True

    def isHidden(self):
        return self._hidden

    def remove(self):
        self.hide()
        self._view.remove(self)

    def showAt(self, location):
        self._location = location
        self._hidden = False
        self.update(0)

    def setPower(self, value, isCurrentVal=False):
        if isCurrentVal:
            self._tension = ((value - getMinPower()) / (getMaxPower(self._smaConnection.getSMAParameters()) - getMinPower()))
        else:
            self._tension = value

        self._powerStr.set(str(int(self._tension*100)))

        # verify duration
        maxdur = self._getMaxActuationDuration(self._smaConnection, self._tension*100)
        if maxdur < self._duration:
            self._durationStr.set(str(int(maxdur)))

    def setDuration(self, value):
        value = int(value)

        # verify duration
        maxdur = self._getMaxActuationDuration(self._smaConnection,self._tension*100)
        if maxdur < value:
            self._duration = maxdur
        else:
            self._duration = value

        self._durationStr.set(str(int(self._duration)))

    def _onChangedPower(self,*args):
        try:
            val = int(self._powerStr.get())

            val = min(max(val, 0), 100) / 100.0
            self.setPower(val)
            self._view.updateView()
        except:
            print("Warning: no number input")


    def _onChangedDuration(self,*args):
        try:
            val = int(self._durationStr.get())

            val = min(max(val, 0), self._getMaxActuationDuration(self._smaConnection,self._tension*100))
            self.setDuration(val)
            self._view.updateView()
        except:
            print("Warning: could not update duration value")
