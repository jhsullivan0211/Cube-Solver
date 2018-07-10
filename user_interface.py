"""Contains the classes needed to build and run the UI."""

import random

import math
import time

from OpenGL.GL import *
from OpenGL.GLU import *

from direct.showbase.ShowBase import ShowBase, LVecBase4f, GeomLines
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
from cube_logic import *

class CubeModel:
    """Contains data and methods for drawing a cube."""

    color_title_map = {"Red": (1, 0, 0),
                       "Blue": (0, 0, 1),
                       "Green": (0, 1, 0),
                       "Yellow": (1, 1, 0),
                       "White": (1, 1, 1),
                       "Black": (0, 0, 0)}

    def __init__(self):
        """Constructor for CubeDrawer.  Generates all of the points of the cube and stores them
        for quick drawing, as well as a map of each sticker to its proper color."""
        self.color_map = {}
        self.sticker_nodepath_map = {}
        self.stickers = CubeModel.generate_stickers()
        for sticker in self.stickers:
            red = random.random()
            green = random.random()
            blue = random.random()

            self.color_map[sticker] = (red, green, blue)


        self.build_model()

    def build_model(self):
        """Draws the node path for the cube."""
        geom_node = GeomNode('gnode')
        index = 0
        for sticker in self.stickers:
            geom_node = GeomNode('gnode')
            sticker_geom = self.get_sticker_geom(sticker, self.color_map[sticker])
            geom_node.addGeom(sticker_geom)
            node_path = render.attachNewNode(geom_node)
            node_path.setTwoSided(True)
            self.sticker_nodepath_map[sticker] = node_path

    def paint_sticker(self, sticker, color):
        self.sticker_nodepath_map[sticker].setColor(color[0], color[1], color[2])
        self.color_map[sticker] = color

    def get_stickers_with_points(self, *points):
        result = []
        for sticker in self.stickers:
            do_continue = False
            for point in points:
                if point not in sticker:
                    do_continue = True
            if do_continue:
                continue
            result.append(sticker)
        return tuple(result)

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

        triangles = GeomTriangles(Geom.UH_static)
        triangles.addVertices(0, 1, 2)
        triangles.addVertices(0, 3, 2)
        triangles.closePrimitive()

        geom = Geom(vertex_data)
        geom.addPrimitive(triangles)

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
                        sticker = tuple([middle, edge, corner,  corner_to_edge[corner]])
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


class MyApp(ShowBase):
    """Runs the UI, which displays the cube."""

    rotation_speed = 1.5

    face_up_points = ((-0.00251, 0.56), (0.1975, 0.453), (0.415, 0.32), (0.395, 0.003), (0.38, -0.287),
                      (0.205, -0.453), (-0.0025, -0.64), (-0.203, -0.45), (-0.375, -0.297), (-0.4, 0),
                      (-0.42, 0.327), (-0.197, 0.467), (-0.005, 0.321), (0.2175, 0.177), (0.21, -0.15),
                      (-0.0025, -0.3271), (-0.215, -0.16), (-0.2231, 0.1771), (0.0011, 0.0101))

    face_down_points = [(0.003, 0.638), (0.197, 0.453), (0.367, 0.297), (0.393, 0.007), (0.42, -0.32),
                        (0.197, -0.457), (-0.002, -0.577), (-0.197, -0.453), (-0.425, -0.323), (-0.397, 0.003),
                        (-0.37, 0.303), (-0.197, 0.45), (0.003, 0.337), (0.207, 0.157), (0.217, -0.167),
                        (-0.01, -0.327), (-0.223, -0.167), (-0.21, 0.16), (0.0, -0.003)]

    face_up_zones = ((0, 1, 12, 11), (11, 12, 17, 10), (12, 13, 18, 17), (1, 2, 13, 12),
                     (10, 17, 16, 9), (17, 18, 15, 16), (13, 14, 15, 18), (2, 3, 14, 13),
                     (9, 16, 7, 8), (16, 15, 6, 7), (14, 5, 6, 15), (3, 4, 5, 14))

    face_down_zones = ((15, 5, 6, 7), (16, 15, 7, 8), (18, 14, 15, 16), (14, 4, 5, 15),
                       (17, 16, 8, 9), (12, 18, 16, 17), (12, 13, 14, 18), (13, 3, 4, 14),
                       (11, 17, 9, 10), (0, 12, 17, 11), (0, 1, 13, 12), (1, 2, 3, 13))

    def __init__(self):
        """Basic constructor for MyApp."""
        ShowBase.__init__(self)
        self.disableMouse()
        self.camera.setPos(0, -10, 0)
        self.cube = CubeModel()
        self.pivot = render.attachNewNode("pivot")
        self.pivot.setPos((0, 0, 0))
        self.camera.wrtReparentTo(self.pivot)
        self.taskMgr.add(self.handle_input, "input")

        self.add_widgets()
        self.sticker_map = {}

        self.accept('z', lambda: print(self.pivot.getHpr()))
        self.accept('x', lambda: self.move_to(Geometry.get_snapped_angles(self.pivot.getHpr())))
        self.accept('v', lambda: print(self.get_nearest_corner()))
        self.accept('mouse1', lambda: self.mouse_click())

    def add_widgets(self):
        """Adds the widgets to the window."""
        self.solve_button = DirectButton(text = ("Solve!"), scale=0.1, pos=(1, 0, 0))
        self.color_select = DirectOptionMenu(text=("Test"), items=["Red", "Blue", "Green", "Yellow", "White", "Black"], scale=0.1, pos=(-1, 0, 0))
        self.solution_label = DirectLabel(text="Here", scale=0.1, pos=(-.8, 0, -.8))


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

        return task.cont

    def move_to(self, angle):
        """Gradually moves the pivot HPR until it is at the specified angles."""
        i = LerpHprInterval(self.pivot, 0.2, Point3(angle[0], angle[1], angle[2]))
        i.start()
        self.sticker_map = self.get_sticker_map(angle)

    def get_nearest_corner(self):
        """Returns the corner nearest to the camera."""
        point = render.getRelativePoint(self.pivot, self.camera.getPos())
        nearest = None
        nearest_dist = math.inf
        for sticker in self.cube.stickers:
            candidate = sticker[2]
            distance = Geometry.get_distance(candidate, point)
            if distance < nearest_dist:
                nearest = candidate
                nearest_dist = distance

        return nearest

    def get_sticker_map(self, angle):
        """Returns a map of each sticker to its oriented position id on the screen currently."""
        sticker_map = {}
        facing_up = angle[1] < 0
        left_axis = 0
        right_axis = 0
        if angle[0] == -45 or angle[0] == 135:
            right_axis = 1
        if angle[0] == 45 or angle[0] == -135:
            left_axis = 1
        if left_axis == right_axis:
            raise Exception("Supplied angle is not correct for generating the sticker map.")

        corner = self.get_nearest_corner()
        corner_stickers = self.cube.get_stickers_with_points(corner)

        for sticker in corner_stickers:
            corner_to_mid = Geometry.subtract_vectors(sticker[0], sticker[2])
            far_corner_point = Geometry.add_vectors(sticker[0], corner_to_mid)
            far_corner = self.cube.get_stickers_with_points(sticker[0], far_corner_point)[0]

            edges = list(self.cube.get_stickers_with_points(sticker[0]))
            edges.remove(far_corner)
            edges.remove(sticker)
            edges = tuple(edges)

            wing_one = edges[0]
            wing_two = edges[1]
            holder = None

            if wing_one[2][2] == wing_two[2][2]:
                if wing_one[2][left_axis] != sticker[2][left_axis]:
                    wing_one, wing_two = wing_two, wing_one
            else:
                if wing_one[2][2] != sticker[2][2]:
                    wing_one, wing_two = wing_two, wing_one

            #NOTE: sticker[0] refers to the point on the sticker that is in the middle of a face of the cube.
            if sticker[0][2] == corner[2]:
                sticker_map[2] = sticker
                sticker_map[0] = far_corner
                sticker_map[1] = wing_one
                sticker_map[3] = wing_two
            if sticker[0][left_axis] == corner[left_axis]:
                sticker_map[5] = sticker
                sticker_map[8] = far_corner
                sticker_map[4] = wing_one
                sticker_map[9] = wing_two
            if sticker[0][right_axis] == corner[right_axis]:
                sticker_map[6] = sticker
                sticker_map[11] = far_corner
                sticker_map[7] = wing_one
                sticker_map[10] = wing_two

        return sticker_map

    def mouse_click(self):
        """The method to perform when the left mouse button is clicked."""
        if self.pivot.getR() != 0:
            return
        if self.mouseWatcherNode.hasMouse():
            mouse_pos_node = self.mouseWatcherNode.getMouse()
            mouse_pos = (mouse_pos_node.getX(), mouse_pos_node.getY())
            zones = []
            points = []
            if self.pivot.getP() == -35:
                zones = MyApp.face_up_zones
                points = MyApp.face_up_points
            if self.pivot.getP() == 35:
                zones = MyApp.face_down_zones
                points = MyApp.face_down_points
            for i in range(len(zones)):
                quad = zones[i]
                built_quad = (points[quad[0]], points[quad[1]],
                              points[quad[2]], points[quad[3]])

                if Geometry.is_within(mouse_pos, built_quad):
                    color = CubeModel.color_title_map[self.color_select.get()]
                    self.cube.paint_sticker(self.sticker_map[i], color)



class Geometry:
    @staticmethod
    def snap_h(angle, deg=-135):
        """Returns an angle for heading, snapped to the nearest orientation such that the angle ensures
        that the cube is in the proper place once the rest of the angles are set."""
        snap_points = [deg, deg + 90, deg + 180, deg + 270]
        for i in range(len(snap_points)):
            if angle < snap_points[i]:
                if abs(angle - snap_points[i]) < abs(angle - snap_points[i - 1]):
                    return snap_points[i]
                else:
                    return snap_points[i - 1]

        return snap_points[-1]

    @staticmethod
    def get_snapped_angles(angles):
        """Returns the angles for heading, pitch, and roll where each is snapped.  The resulting angle puts
        the cube in the proper orientation for clicking."""
        result = [Geometry.snap_h(angles[0]), 35 if angles[1] >= 0 else -35, 0]
        return tuple(result)

    @staticmethod
    def get_distance(vector1, vector2):
        """Returns the distance (scalar) between two vectors."""
        if len(vector1) != len(vector2):
            raise ValueError("Vector dimensions must match.")
        inner_sum = 0
        for i in range(len(vector1)):
            inner_sum += (vector1[i] - vector2[i]) ** 2

        return math.sqrt(inner_sum)

    @staticmethod
    def subtract_vectors(vector1, vector2):
        if len(vector1) != len(vector2):
            raise ValueError("Vector dimensions must match.")

        result = []
        for i in range(len(vector1)):
            result.append(vector1[i] - vector2[i])
        return tuple(result)

    @staticmethod
    def add_vectors(vector1, vector2):
        if len(vector1) != len(vector2):
            raise ValueError("Vector dimensions must match.")

        result = []
        for i in range(len(vector1)):
            result.append(vector1[i] + vector2[i])
        return tuple(result)

    @staticmethod
    def is_within(point, quad):
        """Returns whether the given point lies within the specified quadrilateral."""
        lines = ((0, 1), (1, 2), (2, 3), (3, 0))
        angle_sum = 0
        for line in lines:
            angle = Geometry.angle_CAB(quad[line[0]], point, quad[line[1]])
            angle_sum += angle

        return abs(angle_sum - 2 * math.pi) < 0.001

    @staticmethod
    def angle_CAB(point_c, point_a, point_b):
        """Returns the angle CAB from points C, A, and B."""
        edge_a = Geometry.get_distance(point_c, point_b)
        edge_b = Geometry.get_distance(point_c, point_a)
        edge_c = Geometry.get_distance(point_a, point_b)

        return math.acos(((edge_b ** 2) + (edge_c **2) - (edge_a ** 2)) / (2 * edge_b * edge_c))





app = MyApp()
app.run()
