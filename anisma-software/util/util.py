from shapely.geometry import Polygon
import math
import numpy as np
import itertools

def getDistance(locationA, locationB):
    return math.sqrt((locationA[0]-locationB[0])**2 + (locationA[1]-locationB[1])**2)

def angleBetween(vecA, vecB):
    magM = (magnitude(vecA) * magnitude(vecB))

    if magM == 0:
        return 0

    c = dotProduct(vecA, vecB) / magM
    return math.acos(c) / math.pi * 180.0

def magnitude(vec):
    return math.sqrt(math.pow(vec[0], 2) + math.pow(vec[1], 2))

def getUnitVec(vec):
    mag = magnitude(vec)
    if mag == 0:
        return [0,0]
    return [vec[0]/mag, vec[1]/mag]

def dotProduct(vecA, vecB):
    return vecA[0] * vecB[0] + vecA[1] * vecB[1]

def rotatePoint(x, y, angle, clockwise=False):
    s = math.sin(angle / 180.0 * math.pi)
    c = math.cos(angle / 180.0 * math.pi)

    if clockwise:
        xnew = x * c - y * s;
        ynew = x * s + y * c;
    else:
        xnew = x * c + y * s;
        ynew = -x * s + y * c;

    return [xnew, ynew]

def getCentroid(points):
    if len(points) == 1:
        return points[0]
    if len(points) == 2:
        return [points[0][0] + (points[0][0] - points[1][0])/2, points[0][1] + (points[0][1] - points[1][1])/2]
    P = Polygon(points)
    Pcentroid = P.centroid
    return [Pcentroid.x, Pcentroid.y]

def lerp(a, b, t):
    aa = np.array(a)
    bb = np.array(b)
    return aa*(1 - t) + bb*t

def getSpringDisplacement(stiffness, force):
    return -force / stiffness

def getSpringForce(stiffness, displacement):
    return -stiffness + displacement

# Python program to illustrate the intersection
# of two lists in most simple way
def listIntersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def determineNodeOrientation(node):
    pos = node.getLocation()
    offset = 10
    rotation = 0
    minRotation = 0
    minAvgAngles = 1000

    # as we have 4 slots we only have to check 90 degrees
    for r in range(90):
        r0 = rotatePoint(0, offset, r, clockwise=True)
        r1 = rotatePoint(offset, 0, r, clockwise=True)
        r2 = rotatePoint(0, -offset, r, clockwise=True)
        r3 = rotatePoint(-offset, 0, r, clockwise=True)

        # go through all permutations of connection list orders
        connAngles = []
        permutations = list(itertools.permutations([i for i in range(len(node.getConnections()))], r=len(node.getConnections())))
        for p in permutations:

            takenAngles = [0,1,2,3]
            for i in list(p):
                c = node.getConnections()[i]
                oLocation = c.getOtherNode(node).getLocation()
                rot = [pos[0]-oLocation[0], pos[1]-oLocation[1]]

                a0 = angleBetween(rot, r0)
                a1 = angleBetween(rot, r1)
                a2 = angleBetween(rot, r2)
                a3 = angleBetween(rot, r3)

                # only add open slots that are not used by other SMAs so far
                anglelist = []
                if 0 in takenAngles:
                    anglelist.append(a0)
                if 1 in takenAngles:
                    anglelist.append(a1)
                if 2 in takenAngles:
                    anglelist.append(a2)
                if 3 in takenAngles:
                    anglelist.append(a3)

                anglelist.sort()
                resAngleList = []
                minV = (anglelist.pop(0))
                connAngles.append(minV)
                if minV == a0:
                    takenAngles.remove(0)
                elif minV == a1:
                    takenAngles.remove(1)
                elif minV == a2:
                    takenAngles.remove(2)
                elif minV == a3:
                    takenAngles.remove(3)

            if len(node.getConnections()) < 2:
                avgA = min(connAngles)
            else:
                avgA = max(connAngles)

            if avgA < minAvgAngles:
                minAvgAngles = avgA
                minRotation = r

    return minRotation
