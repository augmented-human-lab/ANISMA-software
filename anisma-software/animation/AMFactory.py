from animation.AMFrame import *
from animation.AMNodeState import *
from animation.AMScene import AMScene
from animation.AMSMAPopUp import AMSMAPopUp

def createInitialScene(allNodes, controller, skinLayer, printLayer):
    scene = AMScene(controller, skinLayer, printLayer)

    # create inital frame
    frame = AMFrame(0)

    for n in allNodes:
        nodeState = AMNodeState(n, n.getLocation())
        frame.setNodeState(nodeState)

    scene.addFrame(frame)
    scene.setCurrentFrame(frame)
    return scene

def createAMSMAPopUp(sma, view, location, scene, clip=None):
    # add PopUpMenu
    popupMenu = AMSMAPopUp(view, location, 320, "Actuation Behavior", scene, sma, clip=clip)
    view.add(popupMenu)

    return popupMenu
