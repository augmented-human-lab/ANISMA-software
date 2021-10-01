from tkinter import *
from shapely.geometry import Point, MultiPoint
from util.util import *
import math

# https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
def roundPolygon(canvas, x, y, sharpness, **kwargs):

    # The sharpness here is just how close the sub-points
    # are going to be to the vertex. The more the sharpness,
    # the more the sub-points will be closer to the vertex.
    # (This is not normalized)
    if sharpness < 2:
        sharpness = 2

    ratioMultiplier = sharpness - 1
    ratioDividend = sharpness

    # Array to store the points
    points = []

    # Iterate over the x points
    for i in range(len(x)):
        # Set vertex
        points.append(x[i])
        points.append(y[i])

        # If it's not the last point
        if i != (len(x) - 1):
            # Insert submultiples points. The more the sharpness, the more these points will be
            # closer to the vertex.
            points.append((float(ratioMultiplier*float(x[i]) + float(x[i + 1]))/float(ratioDividend)))
            points.append((float(ratioMultiplier*float(y[i]) + float(y[i + 1]))/float(ratioDividend)))
            points.append((float(ratioMultiplier*float(x[i + 1]) + float(x[i]))/float(ratioDividend)))
            points.append((float(ratioMultiplier*float(y[i + 1]) + float(y[i]))/float(ratioDividend)))
        else:
            # Insert submultiples points.
            points.append((float(ratioMultiplier*float(x[i]) + float(x[0]))/float(ratioDividend)))
            points.append((float(ratioMultiplier*float(y[i]) + float(y[0]))/float(ratioDividend)))
            points.append((float(ratioMultiplier*float(x[0]) + float(x[i]))/float(ratioDividend)))
            points.append((float(ratioMultiplier*float(y[0]) + float(y[i]))/float(ratioDividend)))
            # Close the polygon
            points.append((x[0]))
            points.append((y[0]))

    return canvas.create_polygon(points, **kwargs,smooth=True,splinesteps=50)

def mapVal(val, fromMin, fromMax, toMin, toMax):
    val = val - fromMin
    fromFraction = val/(fromMax - fromMin)
    toFraction = fromFraction * (toMax - toMin)
    return toFraction + toMin

def drawConnectionWithParams(canvas, start, end, smaparams, zoomlevel, color='black', tension=0.0):
    count = int(smaparams.getNumberOfCoils()*0.65)
    height = mapVal(smaparams.getSpringDiameter(), 1.37, 3.45, 2, 3)
    width = mapVal(smaparams.getWireDiameter(), 0.203, 0.51, 0.5, 1.1)*zoomlevel
    drawConnection(canvas, start, end, count, height, width, color=color, tension=tension)

def drawConnection(canvas, start, end, count, height, width, color='black', tension=0.0):
    dist = getDistance(start, end)

    if dist > 0:
        phaseshift = dist / count
        dirVec = [end[0]-start[0], end[1]-start[1]]
        mag = magnitude(dirVec)
        dirVec = [dirVec[0]/mag, dirVec[1]/mag]

        tensionDist = tension * 0.08 * dist
        startP = start
        for i in range(count):
            tension = (i - count/2)**2 * (math.sqrt(0.1)*(20/count))**2 * (tensionDist/10) - (tensionDist/3)
            endP = [startP[0] + dirVec[0]*phaseshift + dirVec[0]*tension, startP[1] + dirVec[1]*phaseshift + dirVec[1]*tension]
            drawArc(canvas, startP, endP, height, width=width, color=color)
            startP = endP

def drawArc(canvas, start, end, height, width=1.0, color='black'):

    dirVec = [float(end[0])-float(start[0]), float(end[1])-float(start[1])]
    mag = magnitude(dirVec)
    dirVec = [dirVec[0]/mag, dirVec[1]/mag]
    perpDirVec = [dirVec[1], -dirVec[0]]
    dist = float(getDistance(start, end))

    points = []
    resolution = 30
    for i in range(resolution):
        stepX = mapVal(float(i), 0, resolution, 0.0, dist)
        stepY = mapVal(float(i), 0, resolution, 0.0, math.pi*2.0)
        valY = mapVal(math.sin(float(stepY)), 0.0, 1.0, 0.0, float(height))

        pos =  [start[0] + dirVec[0] * stepX, start[1] + dirVec[1] * stepX]
        pos =  [pos[0] + perpDirVec[0] * valY, pos[1] + perpDirVec[1] * valY]

        points.append(pos)

    canvas.create_line(points, width=width, joinstyle=ROUND, capstyle=ROUND, fill=color)

def drawPath(canvas, points, width=1.0):
    startPoint = points[0]
    for i in range(len(points)-1):
        endPoint = points[i]

        canvas.create_line(startPoint[0], startPoint[1], endPoint[0], endPoint[1], width=width, joinstyle=ROUND, capstyle=ROUND,smooth=True,splinesteps=50)

        startPoint = endPoint

def drawLimits(canvas, start, end, minLimit, maxLimit, size, width):
    dirVec = [end[0]-start[0], end[1]-start[1]]
    mag = magnitude(dirVec)
    dirVec = [dirVec[0]/mag, dirVec[1]/mag]
    perpDirVec = [dirVec[1], -dirVec[0]]
    dist = getDistance(start, end)

    mid = [start[0] + dirVec[0] * dist/2, start[1] + dirVec[1] * dist/2]
    lowMidMin = [mid[0] - dirVec[0] * (minLimit/2), mid[1] - dirVec[1] * (minLimit/2)]
    upperMidMin = [mid[0] + dirVec[0] * (minLimit/2), mid[1] + dirVec[1] * (minLimit/2)]
    lowMidMax = [mid[0] - dirVec[0] * (maxLimit/2), mid[1] - dirVec[1] * (maxLimit/2)]
    upperMidMax = [mid[0] + dirVec[0] * (maxLimit/2), mid[1] + dirVec[1] * (maxLimit/2)]

    canvas.create_line(lowMidMin[0] - perpDirVec[0] * size, lowMidMin[1] - perpDirVec[1] * size, lowMidMin[0] + perpDirVec[0] * size, lowMidMin[1] + perpDirVec[1] * size, width=width, joinstyle=ROUND, capstyle=ROUND)
    canvas.create_line(upperMidMin[0] - perpDirVec[0] * size, upperMidMin[1] - perpDirVec[1] * size, upperMidMin[0] + perpDirVec[0] * size, upperMidMin[1] + perpDirVec[1] * size, width=width, joinstyle=ROUND, capstyle=ROUND)
    canvas.create_line(lowMidMax[0] - perpDirVec[0] * size, lowMidMax[1] - perpDirVec[1] * size, lowMidMax[0] + perpDirVec[0] * size, lowMidMax[1] + perpDirVec[1] * size, width=width, joinstyle=ROUND, capstyle=ROUND)
    canvas.create_line(upperMidMax[0] - perpDirVec[0] * size, upperMidMax[1] - perpDirVec[1] * size, upperMidMax[0] + perpDirVec[0] * size, upperMidMax[1] + perpDirVec[1] * size, width=width, joinstyle=ROUND, capstyle=ROUND)


def intersection(circle1, circle2):
    return circle1.intersection(circle2)

def difference(circle1, circle2):
    return circle1.difference(circle2)

class Circle:
    def __init__(self, location, radius):
        self.location = location
        self.radius = radius

def getIntersectionPolygon(circlesInner, circlesOuter, points, looseNode=False):
    pCirclesInner = []
    pCirclesOuter = []
    pCircles = []

    for c in circlesInner:
        pCirclesInner.append(Point(c.location).buffer(c.radius))
    for c in circlesOuter:
        pCirclesOuter.append(Point(c.location).buffer(c.radius))

    for i in range(len(pCirclesInner)):
        pCircles.append(difference(pCirclesOuter[i], pCirclesInner[i]))
    intersectionResult = None

    for j, circle in enumerate(pCircles[:-1]):

        #first loop is 0 & 1
        if j == 0:
            circleA = circle
            circleB = pCircles[j+1]
         #use the result if the intersection
        else:
            circleA = intersectionResult
            circleB = pCircles[j+1]
        intersectionResult = intersection(circleA, circleB)

    # intersection with convex hull of surrounding nodes
    if looseNode:
        hull = getConvexHullPoly(points)
        intersectionResult = intersectionResult.intersection(hull)

    return intersectionResult

def flattenPolyStruct(intersectionResult,interior=False):
    if interior:
        # flatten structure
        result = []
        if not intersectionResult.is_empty:
            if intersectionResult.geom_type == 'MultiPolygon':
                for mp in intersectionResult:
                    newPoly = []
                    for i in mp.interiors:
                        for p in i.coords:
                            for t in p:
                                newPoly.append(t)
                    result.append(newPoly)
            elif intersectionResult.geom_type == 'Polygon':
                newPoly = []
                for i in intersectionResult.interiors:
                    for p in i.coords:
                        for t in p:
                            newPoly.append(t)
                result.append(newPoly)

        return result
    else:
        # flatten structure
        result = []
        if not intersectionResult.is_empty:
            if intersectionResult.geom_type == 'MultiPolygon':
                for mp in intersectionResult:
                    newPoly = []
                    for p in mp.exterior.coords:
                        for t in p:
                            newPoly.append(t)
                    result.append(newPoly)
            elif intersectionResult.geom_type == 'Polygon':
                newPoly = []
                for p in intersectionResult.exterior.coords:
                    for t in p:
                        newPoly.append(t)
                result.append(newPoly)

        return result

def getConvexHullPoly(points):
    multipoints = []
    for p in points:
        multipoints.append(Point(p))

    mp = MultiPoint(multipoints)
    return mp.convex_hull
