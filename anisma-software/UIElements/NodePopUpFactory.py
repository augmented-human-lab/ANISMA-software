from components.SMANodeType import SMANodeType
from UIElements.PopUpMenu import PopUpMenu
from UIElements.PopUpMenuButton import PopUpMenuButton
from components.SMASpringParameters import *

def createNodePopUp(node, view, location):
    # add PopUpMenu
    testBtnB = PopUpMenuButton("Attach Skin", lambda: node.setType(SMANodeType.ELASTIC))
    testBtnC = PopUpMenuButton("Detach Skin", lambda: node.setType(SMANodeType.LOOSE))
    testBtnD = PopUpMenuButton("Delete", lambda: view.remove(node))
    popupMenu = PopUpMenu(view, location, 100, 25, "Node")
    popupMenu.addButton(testBtnB)
    popupMenu.addButton(testBtnC)
    popupMenu.addButton(testBtnD)
    view.add(popupMenu)

    return popupMenu

def toggleSMAType(conn,view):
    params = conn.getSMAParameters()

    if conn.getSMAParameters().getSpringDiameter() == 1.37:
        # switch to big
        newparams = SMASpringParameters(0.381, 8.27, 2.54, 3.5, 6.5, 20)
        newcoils = getOptimalCoilNumber(newparams, params.getExtendedLength(), smacontraction=0.0)
        newparams.setNumberOfCoils(newcoils)
        conn.setSMAParameters(newparams)
    elif conn.getSMAParameters().getSpringDiameter() == 2.54:
        # switch to small
        newparams = SMASpringParameters(0.203, 29.13, 1.37, 3.5, 6.5, 20)
        newcoils = getOptimalCoilNumber(newparams, params.getExtendedLength(), smacontraction=0.0)
        newparams.setNumberOfCoils(newcoils)
        conn.setSMAParameters(newparams)

    view.removeClipsForSMA(conn)
    view.updateView()

def createConnectionPopUp(conn, view, location):
    # add PopUpMenu
    testBtnA = PopUpMenuButton("Switch Type", lambda: toggleSMAType(conn,view))
    testBtnB = PopUpMenuButton("Delete", lambda: view.remove(conn))
    popupMenu = PopUpMenu(view, location, 100, 25, "Connection")
    popupMenu.addButton(testBtnA)
    popupMenu.addButton(testBtnB)
    view.add(popupMenu)

    return popupMenu
