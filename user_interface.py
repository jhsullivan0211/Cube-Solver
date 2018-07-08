"""Contains the classes needed to build and run the UI."""

import random

import math

from OpenGL.GL import *
from OpenGL.GLU import *

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import lookAt
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import LVector3
from panda3d.core import CollisionRay
from direct.task import Task
from panda3d.core import CollisionTraverser, CollisionHandlerQueue
from panda3d.core import CollisionNode, CollisionPolygon
from panda3d.core import Point3
import sys
import os


class CubeModel:
    """Contains data and methods for drawing a cube."""

    def __init__(self):
        """Constructor for CubeDrawer.  Generates all of the points of the cube and stores them
        for quick drawing, as well as a map of each sticker to its proper color."""
        self.color_map = {}
        self.stickers = CubeModel.generate_stickers()
        self.cube_model = self.build_model()

    def build_model(self):
        """Draws the node path for the cube."""

        geom_node = GeomNode('gnode')
        color_list = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0.5, 0, 0), (0, 0.5, 0), (0, 0, 0.5)]
        index = 0
        self.stickers = sorted(self.stickers)
        for sticker in self.stickers:
            sticker_geom = self.get_sticker_geom(sticker, color_list[index])
            index += 1
            if index == len(color_list):
                index = 0
            geom_node.addGeom(sticker_geom)

        node_path = render.attachNewNode(geom_node)
        node_path.setTwoSided(True)
        return node_path

    @staticmethod
    def get_sticker_geom(sticker, sticker_color):
        """Builds and returns a Geom composed of the specified points in sticker, colored the specified color."""

        vertex_format = GeomVertexFormat.getV3c4()
        vertex_data = GeomVertexData("vertices", vertex_format, Geom.UHStatic)
        vertex_data.setNumRows(4)

        vertex_writer = GeomVertexWriter(vertex_data, 'vertex')
        color_writer = GeomVertexWriter(vertex_data, 'color')

        vertex_writer.addData3f(sticker[0])
        color_writer.addData3f(sticker_color)

        vertex_writer.addData3f(sticker[1])
        color_writer.addData3f(sticker_color)

        vertex_writer.addData3f(sticker[2])
        color_writer.addData3f(sticker_color)

        vertex_writer.addData3f(sticker[3])
        color_writer.addData3f(sticker_color)

        color_writer.addData3f(sticker_color)

        prim = GeomTriangles(Geom.UH_static)
        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 3, 1)

        prim.closePrimitive()

        geom = Geom(vertex_data)
        geom.addPrimitive(prim)

        return geom

    @staticmethod
    def scale_sticker(sticker, scalar):
        result = []
        for vertex in sticker:
            scaled = [point * scalar for point in vertex]
            result.append(tuple(scaled))
        return result

    @staticmethod
    def generate_stickers():
        """Generates a tuple of 'stickers', each of which consists of four vertices in space in the following
        order: middle, corner, edge1, edge2."""

        stickers = []
        edge_to_mid = {}
        middles = CubeModel.branch((0, 0, 0))

        for middle in middles:
            corner_to_edge = {}
            edges = CubeModel.branch(middle)
            for edge in edges:
                edge_to_mid[edge] = middle
                corners = CubeModel.branch(edge)
                for corner in corners:
                    if corner in corner_to_edge:
                        sticker = tuple([middle, corner, edge, corner_to_edge[corner]])
                        stickers.append(sticker)
                    else:
                        corner_to_edge[corner] = edge

        return tuple(stickers)

    @staticmethod
    def branch(point):
        """Given a vertex on the cube, gets all points that can be reached by advancing (i.e. moving
        away from zero) in a single axis direction.  This functions in such a way that by calling this
        on the center point it generates middle points, from a middle point it generates the four edge
        points on the same face, and from an edge point it generates the two adjacent corner points."""

        result = []
        for i in range(0, 3):
            if point[i] == 0:
                copy = list(point)
                copy[i] = 1
                result.append(tuple(copy))
                copy2 = list(point)
                copy2[i] = -1
                result.append((tuple(copy2)))
        return result

    def test(self):
        print(self.stickers)


class MyApp(ShowBase):
    """Runs the UI which, which displays the cube."""

    rotation_speed = 1.5

    def __init__(self):
        """Basic constructor for MyApp."""
        ShowBase.__init__(self)
        self.camera.setPos(0, -10, 0)
        self.disableMouse()
        self.camera.setPos(0, -10, 0)
        self.cube = CubeModel()
        self.pivot = render.attachNewNode("pivot")
        self.pivot.setPos((0, 0, 0))
        self.camera.wrtReparentTo(self.pivot)
        self.taskMgr.add(self.handle_input, "input")

        self.add_widgets()

        self.accept('z', lambda: print(self.pivot.getHpr()))
        self.accept('x', lambda: self.move_to(MyApp.get_snapped_angles(self.pivot.getHpr())))
        self.accept('c', lambda: self.pivot.setHpr(45, -45, 0))
        self.accept('v', lambda: self.pivot.setHpr(135, 30, -60))


    def add_widgets(self):
        self.button = DirectButton(text = ("Solve!"), scale=0.1, pos=(1, 0, 0))

        self.radio = DirectOptionMenu(text=("Test"), items=["Red", "Blue", "Green"], scale=0.1, pos=(-1, 0, 0))

        self.label = DirectLabel(text="Here", scale=0.1, pos=(-.8, 0, -.8))
        self.label2 = DirectLabel(text="test", scale=0.1, pos=(-.8, 0, -.9))

    def handle_input(self, task):
        """Listens for input each frame, acting if the input is in process (i.e. a key
        is down, a button pressed, etc.)."""

        if self.mouseWatcherNode.is_button_down('a'):
            self.pivot.setHpr(self.pivot, (MyApp.rotation_speed, 0, 0))
        if self.mouseWatcherNode.is_button_down('d'):
            self.pivot.setHpr(self.pivot, (-MyApp.rotation_speed, 0, 0))
        if self.mouseWatcherNode.is_button_down('w'):
            self.pivot.setHpr(self.pivot, (0, MyApp.rotation_speed, 0))
        if self.mouseWatcherNode.is_button_down('s'):
            self.pivot.setHpr(self.pivot, (0, -MyApp.rotation_speed, 0))
        if self.mouseWatcherNode.is_button_down('e'):
            self.pivot.setHpr(self.pivot, (0, 0, MyApp.rotation_speed))
        if self.mouseWatcherNode.is_button_down('r'):
            self.pivot.setHpr(self.pivot, (0, 0, -MyApp.rotation_speed))

        self.label['text'] = str(self.pivot.getHpr())
        self.label2['text'] = str((self.pivot.getR() == 0 and self.pivot.getP() < 0) or
                                  ((self.pivot.getR() == 180 or self.pivot.getR() == -180) and
                                   self.pivot.getP() < 0))

        return task.cont

    def move_to(self, angle):
        i = LerpHprInterval(self.pivot, 0.2, Point3(angle[0], angle[1], angle[2]))
        i.start()

        #debug

        #end


    @staticmethod
    def snap_hp(angle, deg=-135):
        snap_points = [deg, deg + 90, deg + 180, deg + 270]
        for i in range(len(snap_points)):
            if angle < snap_points[i]:
                if abs(angle - snap_points[i]) < abs(angle - snap_points[i - 1]):
                    return snap_points[i]
                else:
                    return snap_points[i - 1]

        return snap_points[-1]

    @staticmethod
    def snap_r(angle):
        if abs(angle - 180) < abs(angle - 0):
            return 180
        else:
            return 0

    @staticmethod
    def get_snapped_angles(angles):
        result = [MyApp.snap_hp(angles[0]), MyApp.snap_hp(angles[1]), MyApp.snap_r(angles[2])]
        return tuple(result)

app = MyApp()
app.run()
