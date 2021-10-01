from components.Node import Node
from components.Connection import Connection
from components.SMAConnection import SMAConnection
from components.SMASpringParameters import *
from components.constraints.SMAConstraint_MaxLength import SMAConstraint_MaxLength
from components.constraints.SMAConstraint_MinLength import SMAConstraint_MinLength
from components.constraints.SMAConstraint_NoSingleLooseNode import SMAConstraint_NoSingleLooseNode
from components.SMANodeType import *

smaNum = 0

def createConnection(inView, nodeA, nodeB):
    conn = Connection(inView.getCanvas(), nodeA, nodeB)
    inView.add(conn)
    return conn

def createSMAConnection(inView, nodeA, nodeB, params=None, forLength=-1, smacontraction=-1):
    global smaNum
    if params is None:
        params = SMASpringParameters(0.203, 29.13, 1.37, 3.5, 6.5, 70)

    if forLength != -1:
        params.setNumberOfCoils(getOptimalCoilNumber(params, forLength, smacontraction=smacontraction))

    constraints = [SMAConstraint_MaxLength(), SMAConstraint_MinLength(), SMAConstraint_NoSingleLooseNode()]
    smaNum += 1
    conn = SMAConnection(inView.getCanvas(), nodeA, nodeB, params, constraints=constraints, name=("SMA "+str(smaNum)))
    inView.add(conn)

    return conn
