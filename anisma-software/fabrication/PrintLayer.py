from tkinter import *
from render.RenderingObject import *
from components.SMANodeType import *
from shapely.geometry import Point, MultiPoint, MultiPolygon, LineString
from shapely.ops import triangulate
from util.util import *
from util.drawUtil import *
from trimesh.creation import extrude_polygon
import trimesh
from trimesh.scene import Scene
import os
printlayerpy_dir_path = os.path.dirname(os.path.realpath(__file__))

class PrintLayer(RenderingObject):

    def __init__(self, canvas):
        self._canvas = canvas
        self._nodes = []
        self._scene = None
        self._polyLayerDict = {}

    def resetPrintLayers(self):
        self._nodes = []
        self._polyLayerDict = {}

    def setPrintLayers(self, layers):
        self._polyLayerDict = layers

    def getPrintLayers(self):
        return self._polyLayerDict

    def setAnimationScene(self, scene):
        self._scene = scene

    def isInBounds(self, x, y):
        return False

    def addNode(self, smaNode):
        self._nodes.append(smaNode)

    def clear(self):
        self._polygons = []
        self._shapelyPolygons = []
        self._nodes = []

    def isInPrintArea(self, location, padding):
        for layer in self._polyLayerDict:
            if self._polyLayerDict[layer].buffer(padding).contains(Point(location)):
                return True
        return False

    def getThicknessAtPoint(self, location, padding=-1):
        for layer in self._polyLayerDict:
            if padding > -1:
                if self._polyLayerDict[layer].buffer(padding).contains(Point(location)):
                    return float(layer)
            else:
                if self._polyLayerDict[layer].contains(Point(location)):
                    return float(layer)
        return 0.0

    def updateLayer(self, filepath):
        mainMesh = trimesh.Trimesh(vertices=[],
                       faces=[])
        node_mount_blueprint = trimesh.load(printlayerpy_dir_path + '/../fabrication/node_mount.stl')

        for t in self._polyLayerDict:
            p = self._polyLayerDict[t]
            thickness = float(t)
            mainMesh = self.extrudeShapelyPolygon(mainMesh, p, thickness)

        for n in self._nodes:
            pos = n.getLocation()

            thickness = 0
            if self.isInPrintArea(pos, 5):
                thickness = max(thickness, self.getThicknessAtPoint(pos))



            if n.getType() == SMANodeType.ELASTIC:
                # get rotation
                rotation = determineNodeOrientation(n) / 180.0 * math.pi

                # translate rotate and add to main mesh
                node_mount = node_mount_blueprint.copy()
                node_mount = node_mount.apply_transform(trimesh.transformations.rotation_matrix(rotation, (0, 0, 1)))
                if thickness == 0:
                    mainMesh += node_mount.apply_transform(trimesh.transformations.translation_matrix([pos[0],pos[1],0.2]))
                else:
                    mainMesh += node_mount.apply_transform(trimesh.transformations.translation_matrix([pos[0],pos[1],thickness]))

            # ensure that partially overlappingn nodes that get lifted, get a base so that no hangover occurs
            if thickness > 0:
                pa = Point(pos).buffer(7.5)
                mainMesh = self.extrudeShapelyPolygon(mainMesh, pa, thickness)

        # Mirror for correct print
        mainMesh = mainMesh.apply_transform(trimesh.transformations.scale_and_translate(scale=[-1,1,1]))
        mainMesh.export(filepath)
        os.system("open -R "+filepath)


    def extrudePolygon(self, mesh, poly, interior=False, thickness=None):
        if interior:
            newmesh = extrude_polygon(poly, thickness)
            mesh = trimesh.boolean.difference([mesh,newmesh])
        else:
            newmesh = extrude_polygon(poly, thickness)
            mesh = mesh+newmesh

        return mesh

    def extrudeShapelyPolygon(self, mesh, spoly, thickness=None):
        if not spoly.is_empty:
            if spoly.geom_type == 'MultiPolygon':
                for mp in reversed(spoly):
                    mesh = self.extrudeShapelyPolygon(mesh, mp, thickness=thickness)
            elif spoly.geom_type == 'Polygon':
                for p in spoly.interiors:
                    mesh = self.extrudePolygon(mesh, Polygon(p), interior=True, thickness=thickness)
                mesh = self.extrudePolygon(mesh, Polygon(spoly.exterior), thickness=thickness)
        return mesh

    def addCircularPrintArea(self, location, size=7.5, thickness=2, erease=False):
        poly = Point(location).buffer(size)
        self.addPolyPrintArea(poly, thickness, erase=erease)

    def addRectangularPrintArea(self, location, size=7.5, thickness=2, erease=False):
        points = [(location[0]-size, location[1]-size), (location[0]+size, location[1]-size), (location[0]+size, location[1]+size), (location[0]-size, location[1]+size)]
        poly = Polygon(points)
        self.addPolyPrintArea(poly, thickness, erase=erease)

    def addPolyPrintArea(self, poly, thickness, erase=False):
        thickstr = str(thickness)

        if thickstr not in self._polyLayerDict:
            self._polyLayerDict[thickstr] = Polygon()

        # remove from all layers
        for thicknessLayer in self._polyLayerDict:
            self._polyLayerDict[thicknessLayer] = self._polyLayerDict[thicknessLayer].difference(poly)

        # add to thickness layer if its a new piece of print layer
        if not erase:
            self._polyLayerDict[thickstr] = self._polyLayerDict[thickstr].union(poly)

    def drawPolygon(self, poly, interior=False, thickness=None):
        points = []
        for p in poly:
            points.append(p)

        if len(points) > 0:
            pid = None
            if interior:
                pid = self._canvas.create_polygon(points, fill="#FFF", tags="level-4")
            else:
                color = "#54AEFF"
                rgb1 = [209, 233, 255]
                rgb2 = [84, 174, 255]
                if thickness is not None:
                    rg = int(mapVal(thickness, 0.0, 1.0, 225.0, 50.0))
                    color = '#%02x%02x%02x' % (int(mapVal(thickness, 0.0, 1.0, rgb1[0], rgb2[0])), int(mapVal(thickness, 0.0, 1.0,  rgb1[1], rgb2[1])), int(mapVal(thickness, 0.0, 1.0,  rgb1[2], rgb2[2])))
                pid = self._canvas.create_polygon(points, fill=color, tags="level-4")
            self._canvas.lower(pid)

    def drawShapelyPolygon(self, spoly, thickness=None):
        if not spoly.is_empty:
            if spoly.geom_type == 'MultiPolygon':
                for mp in reversed(spoly):
                    self.drawShapelyPolygon(mp,thickness=thickness)
            elif spoly.geom_type == 'Polygon':
                for p in spoly.interiors:
                    self.drawPolygon(p.coords, interior=True, thickness=thickness)
                self.drawPolygon(spoly.exterior.coords, thickness=thickness)


    def update(self, zoomlevel):
        if not (self._scene is not None and self._scene.isPlaying()):
            for thicknessLayer in self._polyLayerDict:
                thickness = float(thicknessLayer)
                self.drawShapelyPolygon(self._polyLayerDict[thicknessLayer], thickness=thickness)
