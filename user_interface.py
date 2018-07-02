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
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import LVector3
from direct.task import Task
import sys
import os


class CubeModel:
    """Contains data and methods for drawing a cube."""
    stickers = None
    color_map = {}
    cube_model = None
    cube_rotation = (0, 0, 0)

    def __init__(self):
        """Constructor for CubeDrawer.  Generates all of the points of the cube and stores them
        for quick drawing, as well as a map of each sticker to its proper color."""

        self.stickers = CubeModel.generate_stickers()
        for sticker in self.stickers:
            red = random.random()
            green = random.random()
            blue = random.random()
            self.color_map[sticker] = tuple([red, green, blue])

        self.draw_cube()

    def draw_cube(self):
        """Draws the cube using the stickers built during construction."""


        geom_node = GeomNode('gnode')
        for sticker in self.stickers:
            sticker_geom = self.draw_sticker(sticker, self.color_map[sticker])
            geom_node.addGeom(sticker_geom)

        node_path = render.attachNewNode(geom_node)
        node_path.setTwoSided(True)
        self.cube_model = node_path
        return node_path


    @staticmethod
    def draw_sticker(sticker, sticker_color):

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

    def rotate(self, rotation):
        new_rotation = tuple(map(sum, zip(rotation, self.cube_rotation)))
        self.cube_rotation = new_rotation
        self.cube_model.setHpr(self.cube_rotation)


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


    key_a = False



    def __init__(self):
        ShowBase.__init__(self)
        self.camera.setPos(0, -10, 0)
        self.disableMouse()
        self.camera.setPos(0, -10, 0)
        self.accept('a', self.rotate_heading_neg)
        self.accept('s', self.rotate_pitch_pos)
        self.accept('d', self.rotate_heading_pos)
        self.accept('w', self.rotate_pitch_neg)

        self.cube = CubeModel()

    def rotate_heading_pos(self):
        self.cube.rotate((10, 0, 0))

    def rotate_heading_neg(self):
        self.cube.rotate((-10, 0, 0))

    def rotate_pitch_neg(self):
        self.cube.rotate((0, -10, 0))

    def rotate_pitch_pos(self):
        self.cube.rotate((0, 10, 0))

    def rotate(task):
        self.cube.rotate((-1, 0, 0))






app = MyApp()
app.run()
