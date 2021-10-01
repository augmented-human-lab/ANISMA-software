from util.globalvars import *
import os
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from ui.InteractionController import InteractionController
from ui.InteractionController import ToolMode, Mode, PencilType
from components.Grid import Grid
from components.SMANode import SMANode
from render.Cursor import Cursor
from render.ViewManager import ViewManager
from render.UIViewTopBar import UIViewTopBar
from components.NodeFactory import *
from components.ConnectionFactory import *
from components.SkinLayerFactory import *
from components.UIScale import UIScale
from components.Legend import Legend
from fabrication.PrintLayer import PrintLayer
from UIElements.Button import Button
from UIElements.TabBarButton import TabBarButton
from UIElements.RadioButtonGroup import RadioButtonGroup
from animation.AMFactory import *
from animation.AMTimelineView import AMTimelineView
from animation.AMTimeSlider import AMTimeSlider
from animation.AMTimeLineViewIC import AMTimeLineViewIC
from UIElements.Anchor import Anchor
from UIElements.UIToolBoxView import UIToolBoxView
from UIElements.UIToolBoxIC import UIToolBoxIC
from UIElements.ToolBoxItems.TBISMAModule import TBISMAModule
from UIElements.ToolBoxItems.TBIPencil import TBIPencil
from UIElements.ToolBoxItems.TBIEraser import TBIEraser
from UIElements.ToolBoxItems.TBIMeasurementTape import TBIMeasurementTape
from UIElements.ToolBoxItems.TBICustomSMA import TBICustomSMA
from controller.Controller import Controller
import pickle
import os, sys

mainpy_dir_path = os.path.dirname(os.path.realpath(__file__))

print("Running ANISMA Studio on", sys.platform)

# Setup windows
window = Tk()
window.tk.call('tk', 'scaling', 1.0)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_width = int(screen_width*0.7)
window_height = int(screen_height*0.75)
window_x = screen_width / 2 - window_width / 2
window_y = screen_height / 2 - window_height / 2
prusai3mk3_dimX = 210
prusai3mk3_dimY = 200
geometry_str = str(window_width) + "x" + str(window_height) + "+" + str(int(window_x)) + "+" + str(int(window_y))

window.geometry(geometry_str)
window.title("ANISMA Studio")

# Create UI toolbar canvas
ui_canvas = Canvas(window, width=window_width, height=72+48, bd=0, highlightthickness=0, background="#12333D")
ui_canvas.pack(fill=BOTH, expand=0)
ui = UIViewTopBar(ui_canvas)

# Create main drawing canvas
main_canvas = Canvas(window, width=window_width, height=50, bd=0, highlightthickness=0)
main_canvas.pack(fill=BOTH, expand=1)

view = ViewManager(main_canvas, [int(-window_width/2.15), int(-window_height/2+40)])

grid = Grid(main_canvas, 2000, 2000, printArea=[prusai3mk3_dimX, prusai3mk3_dimY])
cursor = Cursor(main_canvas, view)

legend_loc_design = [17, 300]
scale_loc_design = [36, 300-43-200]
legend_loc_animation = [17, 300+264+41]
scale_loc_animation = [36, 300-43-200+264+41]

scale = UIScale(main_canvas, scale_loc_design)
legend = Legend(main_canvas, legend_loc_design)

printLayer = PrintLayer(main_canvas)


view.add(grid)
view.add(cursor)
view.add(scale)
view.add(legend)
view.add(printLayer)

# controller
anismaPort = Controller.findANISMAControllerDevice(None)

controller = Controller(anismaPort)
controller.connect()

# ADD SKIN Layer
skinLayer = None

# Create animation timeline canvas
amTimeline_canvas = Canvas(main_canvas, width=1000, height=264+41, bd=0, highlightthickness=0)
amTimeline_canvas.pack(side=BOTTOM, fill=X, expand=0)
animationScene = createInitialScene([], controller, skinLayer, printLayer)
view.setScene(animationScene)
printLayer.setAnimationScene(animationScene)
amTimeline = AMTimelineView(amTimeline_canvas, animationScene)
timeLineIC = AMTimeLineViewIC(window, amTimeline_canvas, amTimeline, animationScene, view, controller)

# ToolBox
toolbox_canvas = Canvas(main_canvas, width=80, height=325, bd=0, highlightthickness=0)
toolboxView = UIToolBoxView(toolbox_canvas, [17,137-120])
toolboxIC = UIToolBoxIC(window, toolbox_canvas, toolboxView, view)


# add interaction controller that defines point and click behavior
radioMode = RadioButtonGroup()
ic = InteractionController(window, main_canvas, view, ui, toolboxView, amTimeline, cursor, radioMode, animationScene, printLayer, grid = grid)

### create UIElements
# Create button group that switches input mode

# button callbacks
def cb_nodes(btn, ic):
    ic.setToolMode(ToolMode.PLACE_NODES)

def cb_mani(btn, ic):
    ic.setToolMode(ToolMode.MANIPULATE)

def cb_module(btn, ic):
    ic.setToolMode(ToolMode.PLACE_MODULE)

def cb_fabricate(btn, ic):
    objs = view.getAllObjects()
    printLayer.clear()
    for o in objs:
        if isinstance(o, SMANode):
            printLayer.addNode(o)
    printLayer.updateLayer()
    view.updateView()

# Toolbox
c30_spring_s = SMASpringParameters(0.203, 29.13, 1.37, 3.5, 6.5, 30)
def cb_c30spressed(btn, ic):
    ic.setToolMode(ToolMode.PLACE_MODULE, smaparams=c30_spring_s)

c50_spring_s = SMASpringParameters(0.203, 29.13, 1.37, 3.5, 6.5, 50)
def cb_c50spressed(btn, ic):
    ic.setToolMode(ToolMode.PLACE_MODULE, smaparams=c50_spring_s)

c30_spring_m = SMASpringParameters(0.381, 8.27, 2.54, 3.5, 6.5, 30)
def cb_c30mpressed(btn, ic):
    ic.setToolMode(ToolMode.PLACE_MODULE, smaparams=c30_spring_m)

c50_spring_m = SMASpringParameters(0.381, 8.27, 2.54, 3.5, 6.5, 50)

def cb_c50mpressed(btn, ic):
    if btn.isActive():
        ic.setToolMode(ToolMode.PLACE_MODULE, smaparams=c50_spring_m)
    else:
        ic.setToolMode(ToolMode.MANIPULATE, smaparams=c50_spring_m)

def cb_drawRECTPrintLayer(btn, ic):
    ic.setToolMode(ToolMode.DRAW_PRINTLAYER, pencilType=PencilType.RECTANGULAR)

def cb_drawROUNDPrintLayer(btn, ic):
    ic.setToolMode(ToolMode.DRAW_PRINTLAYER, pencilType=PencilType.RECTANGULAR)

def cb_measurementTape(btn, ic):
    if ic.getToolMode() is ToolMode.MEASUREMENT_TAPE:
        ic.setToolMode(ToolMode.MANIPULATE)
    else:
        ic.setToolMode(ToolMode.MEASUREMENT_TAPE)

item_c30s = TBISMAModule(toolbox_canvas, mainpy_dir_path + "/icons/standard_sma_colour@2x.png", c30_spring_s, ic=ic)
item_addconnection = TBICustomSMA(toolbox_canvas, mainpy_dir_path + "/icons/custom_sma_colour@2x.png", c30_spring_s, ic=ic)
item_drawRectPrintLayer = TBIPencil(toolbox_canvas, mainpy_dir_path + "/icons/draw_rigid_colour@2x.png", ic=ic)
item_drawRoundPrintLayer = TBIEraser(toolbox_canvas, mainpy_dir_path + "/icons/erase_rigid_colour@2x.png", ic=ic)
item_measurementTape = TBIMeasurementTape(toolbox_canvas, mainpy_dir_path + "/icons/measure_colour@2x.png", callback=cb_measurementTape, ic=ic)


toolboxView.addListItem(item_c30s)
toolboxView.addListItem(item_addconnection)
toolboxView.addListItem(item_drawRectPrintLayer)
toolboxView.addListItem(item_drawRoundPrintLayer)
toolboxView.addListItem(item_measurementTape)

def getRawFileName(filepath):
    base = os.path.basename(filepath)
    return os.path.splitext(base)[0]

# Mode Buttons
def cb_design(btn, ic):
    ic.setMode(Mode.DESIGN)
    amTimeline.show(False)
    toolboxView.show(True)
    animationScene.stop()

    scale.setLocation(scale_loc_design)
    legend.setLocation(legend_loc_design)

    timeLineIC.getControllerCheckBox().deselect()
    timeLineIC.cb_contract_click()

    view.updateView()

def cb_animate(btn, ic):
    ic.setMode(Mode.ANIMATE)
    amTimeline.show(True)
    toolboxView.show(False)

    scale.setLocation(scale_loc_animation)
    legend.setLocation(legend_loc_animation)

    nodes = []
    # prepare export
    objs = view.getAllObjects()
    for o in objs:
        if isinstance(o, SMANode):
            nodes.append(o)

    controller.assignPolarities(nodes)
    controller.assignPhases(nodes)
    controller.assignPins(nodes)

    view.updateView()
    amTimeline.updateView()

def cb_fabricate(btn, ic):
    run_through_simulation = animationScene.animationHasRun()
    errors_detected = animationScene.hasAnimationRunWithError()
    do_export = False

    if not run_through_simulation:
        MsgBox = messagebox.askquestion('Warning: Simulation Not Run', 'It is recommended to run the simulation at least once after making any changes.\n\n(This helps to detect potential problems before the physical realization.)\n\nDo you still wish to continue to export?', icon = 'warning')
        if MsgBox == 'yes':
            do_export = True
    else:
        if errors_detected:
            MsgBox = messagebox.askquestion('Warning: Design Issue Detected', "It is recommended to fix any potential design issues before exporting.\n\nDo you still wish to continue to export?", icon = 'warning')
            if MsgBox == 'yes':
                do_export = True
        else:
            do_export = True

    if do_export:
        filename = filedialog.asksaveasfilename(initialdir = "~/Downloads/", initialfile = "ANISMA_exportfile.stl", title = "Select file", filetypes = (("3D STL Files","*.stl"),("all files","*.*")))

        if filename != '':
            animationScene.stop()

            # prepare export
            objs = view.getAllObjects()
            printLayer.clear()
            for o in objs:
                if isinstance(o, SMANode):
                    printLayer.addNode(o)

            printLayer.updateLayer(filename)
            view.updateView()

def cb_new(btn, ic):
    # view
    objects = view.getAllNonPersistantObjects()
    for o in objects:
        view.remove(o)

    # printlayer
    printLayer.resetPrintLayers()

    ui.setProjectName("Untitled")

    view.updateView()
    ui.updateView()
    amTimeline.updateView()

def cb_save(btn, ic):
    filename = filedialog.asksaveasfilename(initialdir = mainpy_dir_path + "/",title = "Select file",filetypes = (("ANISMA save files","*.anismasav"),("all files","*.*")))

    if filename != '':
        # view
        objects = view.getAllNonPersistantObjects()

        # scene
        sceneTracks = animationScene.getTracks()

        # printlayer
        printlayers = printLayer.getPrintLayers()

        with open(filename, "wb") as f:
            pickle.dump([objects, sceneTracks, printlayers], f)

        ui.setProjectName(getRawFileName(filename))
        view.updateView()
        ui.updateView()
        amTimeline.updateView()

def cb_load(btn, ic):
    filename = filedialog.askopenfilename(initialdir = mainpy_dir_path + "/",title = "Select file",filetypes = (("ANISMA save files","*.anismasav"),("all files","*.*")))

    if filename != '':
        # reset
        cb_new(btn, ic)

        with open(filename, "rb") as f:
            objects, sceneTracks, printlayers = pickle.load(f)

            # view
            for o in objects:
                view.add(o)
                if isinstance(o, SMANode):
                    o._skinNodes = []
                o.setCanvas(main_canvas)

            # scene
            animationScene.setTracks(sceneTracks)

            # printlayer
            printLayer.setPrintLayers(printlayers)

        ui.setProjectName(getRawFileName(filename))
        view.updateView()
        ui.updateView()
        amTimeline.updateView()

btn_prj_new = Button(ui_canvas, [16+60, 16+20], 120, 40, "New", callback=cb_new, ic=ic, radioGroup=None, anchor=Anchor.TOPLEFT)
btn_prj_load = Button(ui_canvas, [152+60, 16+20], 120, 40, "Load", callback=cb_load, ic=ic, radioGroup=None, anchor=Anchor.TOPLEFT)
btn_prj_save = Button(ui_canvas, [1440-(1168+60), 16+20], 120, 40, "Save", callback=cb_save, ic=ic, radioGroup=None, anchor=Anchor.TOPRIGHT)

btn_design = TabBarButton(ui_canvas, [-(721-552)/2, 80+15], 166.5, 30, "Design", callback=cb_design, ic=ic, radioGroup=radioMode, anchor=Anchor.TOPCENTER)
btn_animate = TabBarButton(ui_canvas, [+(721-552)/2, 80+15], 166.5, 30, "Animate", callback=cb_animate, ic=ic, radioGroup=radioMode, anchor=Anchor.TOPCENTER)
btn_fabricate = Button(ui_canvas, [1440-(1304+60), 16+20], 120, 40, "Export", callback=cb_fabricate, ic=ic, anchor=Anchor.TOPRIGHT)

# Set initial mode to place nodes
ic.setToolMode(ToolMode.MANIPULATE)
ic.setMode(Mode.DESIGN)

# add to ui bar
ui.add(btn_prj_new)
ui.add(btn_prj_load)
ui.add(btn_prj_save)
ui.add(btn_design)
ui.add(btn_animate)
ui.add(btn_fabricate)


# add timeline view components
am_slider = AMTimeSlider(amTimeline_canvas, animationScene, amTimeline)
amTimeline.add(am_slider)
animationScene.setTimelineView(amTimeline)
animationScene.setMainView(view)
animationScene.setWindow(window)


def setSimulationVars(v1, v2, v3, v4, v5, v6, v7):
    w1.set(v1)
    w2.set(v2)
    w3.set(v3)
    w4.set(v4)
    w5.set(v5)
    w6.set(v6)

    global globalvars
    stiffness = 1
    globalvars.collisionconstraint = v1
    globalvars.smapoweramplifier = v4
    globalvars.collisionconstraint_dist = v5

    E = v2*stiffness*10 # Pa = kg * m^-1 * s^-2
    thickness = 0.001  # in meteres
    skin_mass = 1.02/1000 # in kg 1.02 g/cm2


    globalvars.skin_sprinconstant = 2 * (5/16)*thickness*E  # in kg * s^-2
    globalvars.skin_sprinconstant_diag = (7/16)*thickness*E # in kg * s^-2

    globalvars.skin_damping = v6 /1000
    globalvars.skin_damping = 2*math.sqrt(globalvars.skin_mass*globalvars.skin_sprinconstant) * globalvars.skin_damping #
    globalvars.skin_damping_diag = 2*math.sqrt(globalvars.skin_mass*globalvars.skin_sprinconstant_diag) * globalvars.skin_damping  #

    globalvars.anchor_sprinconstant = 0.01*v3
    globalvars.sma_damping = v7

def update_skin_params(event = None):
    global globalvars
    globalvars.sma_damping = w7.get()

w1 = Scale(main_canvas, from_=0.0, to=2.0, resolution=.01, orient='horizontal',command=update_skin_params)
w2 = Scale(main_canvas, from_=0.0, to=500000.0, resolution=1.0, orient='horizontal',command=update_skin_params)
w3 = Scale(main_canvas, from_=0.0, to=500000.0, resolution=1.0, orient='horizontal',command=update_skin_params)
w4 = Scale(main_canvas, from_=0.0, to=30.0, resolution=.1, orient='horizontal',command=update_skin_params)
w5 = Scale(main_canvas, from_=0.0, to=4.0, resolution=.1, orient='horizontal',command=update_skin_params)
w6 = Scale(main_canvas, from_=0.0, to=0.001, resolution=.00001, orient='horizontal',command=update_skin_params)
w7 = Scale(main_canvas, from_=0.00001, to=0.5, resolution=.00001, orient='horizontal',command=update_skin_params)

setSimulationVars(0.15, 14706, 588, 2.2*40, 1.0, 0.00004, 0.1)

# initially update views
amTimeline.show(False)
view.updateView()
ui.updateView()
amTimeline.updateView()
toolboxView.updateView()

# enter tkinter mainloop
window.mainloop()
