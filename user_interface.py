"""Contains the classes needed to build and run the GUI.

The GUI for this 2x2x2 cube solving application consists of a window, a 3D graphic representation of a 2x2x2 cube,
a selection for the color to apply to a sticker on click, a solve button to start the solving algorithm, a label
to display the solution, and various helper labels to clarify the cube nomenclature and show the orientation of the
cube.

This module contains the main GUI class "MyApp", which draws all of the widgets and the cube onto a window using the
Panda3d graphics library.  Additionally, it contains a CubeModel class which contains the data of the cube, a
CubeController class to mediate between this module and the cube_logic.py module, and a Geometry utility class."""

import math
from direct.showbase.ShowBase import ShowBase, WindowProperties
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import GeomNode
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from cube_logic import *


class CubeModel:
    """Contains data and methods for drawing a cube."""

    color_title_map = {"Red": (0.8, 0, 0),
                       "Blue": (0, 0, 0.8),
                       "Green": (0, 0.6, 0.3),
                       "Yellow": (1, 1, 0),
                       "White": (1, 1, 1),
                       "Black": (0, 0, 0)}

    blank_color = (0.3, 0.3, 0.3)
    back_color = (0.2, 0.2, 0.2)
    sticker_scale = 0.9

    def __init__(self):
        """Constructor for CubeModel."""

        self.color_map = {}
        self.sticker_nodepath_map = {}
        self.stickers = CubeModel.__generate_stickers()
        for sticker in self.stickers:
            self.color_map[sticker] = CubeModel.blank_color

        self.build_model()

    def build_model(self):
        """Draws the node paths for the cube."""
        for sticker in self.stickers:
            geom_node = GeomNode('gnode')

            sticker_geom = self.__build_sticker_geom(sticker, self.color_map[sticker], CubeModel.sticker_scale)
            geom_node.addGeom(sticker_geom)
            node_path = render.attachNewNode(geom_node)
            node_path.setTwoSided(True)
            self.sticker_nodepath_map[sticker] = node_path
            frame_sticker = tuple(Geometry.scale_vector(point, 0.99) for point in sticker)
            frame_node = GeomNode('framenode')
            frame_geom = self.__build_sticker_geom(frame_sticker, CubeModel.back_color, 1)
            frame_node.addGeom(frame_geom)
            frame_path = render.attachNewNode(frame_node)
            frame_path.setTwoSided(True)

    def paint_sticker(self, sticker, color):
        """Paints the specified sticker the specified color.

        Parameters
        ----------
        sticker: tuple
                 A size-4 tuple consisting of the middle, edge, corner, and edge points, respectively.

        color:  tuple
                The RGB values of the color to paint the sticker.
        """
        self.sticker_nodepath_map[sticker].setColor(color[0], color[1], color[2])
        self.color_map[sticker] = color

    def get_stickers_with_points(self, *points):
        """Returns all stickers that contain the specified points.

        Parameters
        ----------
        *points: *int
                 A variable number of points, where the returned sticker contains each point listed.
        """
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
    def __build_sticker_geom(sticker, sticker_color, scalar=1):
        """Builds and returns a Geom composed of the specified points in sticker, colored the specified color.

        Parameters
        ----------
        sticker: tuple
                 A size-4 tuple consisting of the middle, edge, corner, and edge points, respectively.

        sticker_color: tuple
                       The RGB values for the sticker color.

        scalar:  float, optional
                 The scale of the sticker from 0 to 1, where 1 has the sticker cover the entier cubie.
                 Defaults to 1.

        """

        sticker = CubeModel.__scale_sticker(sticker, scalar)
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
    def __scale_sticker(sticker, scalar):
        """Given a sticker (tuple of 4 points), returns the same sticker, but scaled by the specified amount.

        Paramters
        ---------
        sticker: tuple
                 A size-4 tuple consisting of the middle, edge, corner, and edge points, respectively.

        scalar:  The amount to scale the sticker quad.

        """
        result = []

        for i in range(len(sticker)):
            j = i + 2
            if j >= len(sticker):
                j -= len(sticker)

            movement = Geometry.subtract_vectors(sticker[j], sticker[i])
            movement = Geometry.scale_vector(movement, 1 - scalar)
            new_point = Geometry.add_vectors(sticker[i], movement)
            result.append(new_point)
        return tuple(result)

    @staticmethod
    def __generate_stickers():
        """Generates a tuple of 'stickers', each of which consists of four vertices in space in the following
        order: middle, edge, corner, edge.  Does not provide a guarantee of which edge point is which."""

        stickers = []
        edge_to_mid = {}
        middles = CubeModel.__branch((0, 0, 0))

        for middle in middles:
            corner_to_edge = {}
            edges = CubeModel.__branch(middle)
            for edge in edges:
                edge_to_mid[edge] = middle
                corners = CubeModel.__branch(edge)
                for corner in corners:
                    if corner in corner_to_edge:
                        sticker = middle, edge, corner,  corner_to_edge[corner]
                        stickers.append(sticker)
                    else:
                        corner_to_edge[corner] = edge

        return tuple(stickers)

    @staticmethod
    def __branch(point):
        """Given a vertex on the cube, gets all points that can be reached by advancing (i.e. moving
        away from zero) in a single axis direction.  This functions in such a way that by calling this
        on the center point it generates middle points, from a middle point it generates the four edge
        points on the same face, and from an edge point it generates the two adjacent corner points.

        Parameters
        ----------
        point:  tuple
                The point from which to branch.
        """

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


class Geometry:
    """Contains some useful geometry functions applicable to cube drawing."""
    @staticmethod
    def snap_h(angle, deg=-135):
        """Returns an angle for heading, snapped to the nearest orientation such that the angle ensures
        that the cube is in the proper place once the rest of the angles are set.

        Parameters
        ----------
        angle: float
               The angle to snap.

        deg:  float, optional
              The offset of the snap, such that the snap points will start at the deg, and increment by 90 all the
              way around the axis."""

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
        """Returns the Euler rotation angles for heading, pitch, and roll where each is sngle is snapped, i.e. the
        rotation is forced to be angles of (45N, +-35, 0) where N is some integer.  The resulting rotation if used
        for the cube puts the cube in the proper orientation for clicking.

        Parameters
        ----------
        angles: iterable of angles
                A set of three angles corresponding to a (heading, pitch, roll) Euler rotation.
        """
        return Geometry.snap_h(angles[0]), -MyApp.origin_rot[1] if angles[1] >= 0 else MyApp.origin_rot[1], 0


    @staticmethod
    def get_distance(vector1, vector2):
        """Returns the distance (scalar) between two vectors.

        Parameters
        ----------
        vector1: tuple of float
                 The first vector.

        vector2: tuple of float
                 The second vector.
        """


        if len(vector1) != len(vector2):
            raise ValueError("Vector dimensions must match.")
        inner_sum = 0
        for i in range(len(vector1)):
            inner_sum += (vector1[i] - vector2[i]) ** 2

        return math.sqrt(inner_sum)

    @staticmethod
    def subtract_vectors(vector1, vector2):
        """Returns the result of the subtraction of the second vector from the first vector.

        Parameters
        ----------
        vector1:  tuple of float
                  The first vector.

        vector2:  tuple of float
                  The second vector.
        """
        if len(vector1) != len(vector2):
            raise ValueError("Vector dimensions must match.")

        return tuple(v1 - v2 for v1, v2 in zip(vector1, vector2))

    @staticmethod
    def add_vectors(vector1, vector2):
        """Returns the result of the addition of the second vector to the first vector.

        Parameters
        ----------
        vector1:  tuple of float
                  The first vector.

        vector2:  tuple of float
                  The second vector.
        """
        if len(vector1) != len(vector2):
            raise ValueError("Vector dimensions must match.")

        return tuple(v1 + v2 for v1, v2 in zip(vector1, vector2))


    @staticmethod
    def scale_vector(vector, scalar):
        """Returns the result of scaling the specified vector by the specified scalar.

        Parameters
        ----------
        vector:   tuple of float
                  The vector to scale.

        scalar:  float
                 The scalar to scale the vector by.
        """
        return tuple(v * scalar for v in vector)

    @staticmethod
    def is_within(point, quad):
        """Returns whether the given point lies within the specified quadrilateral.

        Parameters
        ----------
        point: tuple of float
               The (x, y) point to check.

        quad:  tuple of tuple of float:
               The four (x, y) points defining the quadrilateral that the specified point could lie within.
        """
        lines = ((0, 1), (1, 2), (2, 3), (3, 0))
        angle_sum = 0
        for line in lines:
            angle = Geometry.angle_CAB(quad[line[0]], point, quad[line[1]])
            angle_sum += angle

        return abs(angle_sum - 2 * math.pi) < 0.001

    @staticmethod
    def angle_CAB(point_c, point_a, point_b):
        """Returns the angle CAB from points C, A, and B.

        Parameters
        ----------
        point_c: tuple of float
                 Point C in the angle CAB.

        point_a: tuple of float:
                 Point A in the angle CAB; the middle vertex of the angle.

        point_b: tuple of float:
                 Point B in the angle CAB.

        """
        edge_a = Geometry.get_distance(point_c, point_b)
        edge_b = Geometry.get_distance(point_c, point_a)
        edge_c = Geometry.get_distance(point_a, point_b)

        acos_input = ((edge_b ** 2) + (edge_c **2) - (edge_a ** 2)) / (2 * edge_b * edge_c)

        if acos_input < -1:
            acos_input = -1
        if acos_input > 1:
            acos_input = 1
        return math.acos(acos_input)


class CubeController:
    """A mediator between the GUI of this module (specifically the CubeModel class) and the cube_logic module which
    has the capability to build and solve the logical cube."""

    _already_solved_message = "Cube is already solved."
    _unsolvable_message = "The cube cannot be solved."

    def __init__(self, cube_model):
        """Basic constructor for the CubeController class.

        Parameters
        ----------
        cube_model:  CubeModel
                     The model from which to get color data to build the logical cube.
        """
        self.cube_model = cube_model
        color_map = cube_model.color_map
        conversion = (19, 13, 5, 17, 4, 9, 16, 8, 0, 18, 1, 12,
                      23, 7, 15, 21, 11, 6, 20, 2, 10, 22, 14, 3)
        self.colors = []
        stickers = cube_model.stickers
        for i in conversion:
            raw_color = color_map[stickers[i]]
            color_string = ""
            for key, value in CubeModel.color_title_map.items():
                if value == raw_color:
                    color_string = key
            self.colors.append(color_string)

    def solve(self):
        """Attempts to solve the cube, returning the solution if successful or messages indicating that either
        the cube is unsolvable or it is already solved."""

        try:
            logical_cube = CubeBuilder.get_cube_from_colors(self.colors)
            solution = Solver.get_solution(logical_cube, Cube.new_cube())
            if len(solution) == 0:
                return CubeController._already_solved_message

            solution_string = ""
            for i in range(len(solution)):
                solution_string += solution[i]
                if i < len(solution) - 1:
                    solution_string += ", "
            return solution_string
        except ValueError:
            return CubeController._unsolvable_message


class MyApp(ShowBase):
    """Runs the GUI, which displays the cube, a selection for color, a solve button, a lebel for the solution,
    and various helpful labels for interpreting the results correctly."""

    rotation_speed = 120
    mouse_speed_factor = 1

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

    origin_rot = (-45, -35, 0)

    def __init__(self):
        """Basic constructor for MyApp."""
        ShowBase.__init__(self)

        self.disableMouse()
        self.camera.setPos(0, -10, 0)
        self.cube = CubeModel()
        self.pivot = render.attachNewNode("pivot")
        self.pivot.setPos((0, 0, 0))
        self.camera.wrtReparentTo(self.pivot)
        self.pivot.setHpr(MyApp.origin_rot)
        self.moving = False
        self.add_widgets()
        self.sticker_map = {}
        self.move_to(MyApp.origin_rot, self.update_sticker_map)
        self.accept('mouse1', self.mouse_click)
        self.previous_click = None
        self.taskMgr.add(self.lock_format, "format lock")

    def add_widgets(self):
        """Adds the widgets to the window."""

        self.solve_button = DirectButton(text = "Solve!",
                                         command=self.solve_setup,
                                         scale=0.1,
                                         pos=(1, 0, 0.7))

        self.color_select = DirectOptionMenu( items=["Red", "Blue", "Green", "Yellow", "White", "Black"],
                                             scale=0.1,
                                             pos=(-1.2, 0, 0.7))

        self.solution_label = DirectLabel(text="",
                                          scale=0.1,
                                          pos=(0, 0, -.8),
                                          frameColor=self.getBackgroundColor())

        self.left_label = DirectLabel(text="Left",
                                      scale=0.1,
                                      pos=(-0.45, 0, -0.6),
                                      frameColor=self.getBackgroundColor())

        self.front_label = DirectLabel(text="Front",
                                      scale=0.1,
                                      pos=(0.45, 0, -0.6),
                                      frameColor=self.getBackgroundColor())

        self.up_label = DirectLabel(text="Up",
                                      scale=0.1,
                                      pos=(0, 0, 0.65),
                                      frameColor=self.getBackgroundColor())

        self.case_label = DirectLabel(text="Uppercase: Clockwise\n" +
                                           "Lowercase: Counter-clockwise",
                                      scale=0.05,
                                      pos=(0, 0, -0.9),
                                      frameColor=self.getBackgroundColor())

        self.hide_labels()

    def lock_format(self, task):
        if self.win.getXSize() != 800 or self.win.getYSize() != 600:
            wp = WindowProperties()
            wp.setSize(800, 600)
            self.win.requestProperties(wp)
        return task.cont

    def solve_setup(self):
        self.solution_label["text"] = "Thinking..."
        self.move_to(MyApp.origin_rot, self.solve_cube)

    def hide_labels(self):
        """Hides the labels that may be hidden."""

        self.left_label.hide()
        self.up_label.hide()
        self.front_label.hide()
        self.case_label.hide()
        self.solution_label["text"] = ""

    def show_labels(self):
        """Shows the labels that may be hidden."""

        self.left_label.show()
        self.front_label.show()
        self.up_label.show()
        self.case_label.show()

    def solve_cube(self):
        """Solves the cube currently drawn on the graphical cube model for this application."""
        self.solution_label["text"] = "Thinking..."
        controller = CubeController(self.cube)
        solution = controller.solve()
        self.solution_label["text"] = solution
        self.show_labels()

    def mouse_click(self):
        """The method to perform when the left mouse button is clicked.  Creates a task that runs each tick
        while the mouse is clicked which updates the rotation of the cube by the position of the mouse, and
        also checks to see if a sticker is clicked when in its fixed position, coloring that sticker if it is
        with the color specified by the color selection widget of the GUI."""

        if self.mouseWatcherNode.hasMouse():
            position = self.mouseWatcherNode.getMouse()
            mouse_pos = (position.getX(), position.getY())
            zones = []
            points = []
            if self.pivot.getP() == -35:
                zones = MyApp.face_up_zones
                points = MyApp.face_up_points
            if self.pivot.getP() == 35:
                zones = MyApp.face_down_zones
                points = MyApp.face_down_points
            clicked_sticker = False
            for i in range(len(zones)):
                quad = zones[i]
                built_quad = (points[quad[0]], points[quad[1]],
                              points[quad[2]], points[quad[3]])
                if Geometry.is_within(mouse_pos, built_quad):
                    color = CubeModel.color_title_map[self.color_select.get()]
                    self.cube.paint_sticker(self.sticker_map[i], color)
                    clicked_sticker = True
            if not clicked_sticker:
                self.previous_click = (position[0], position[1])
                self.taskMgr.remove("click")
                self.taskMgr.add(self.mouse_down_loop, "click")

    def mouse_down_loop(self, task):
        """Called every tick while the mouse is down.  Updates the rotation based on how much the mouse has moved
        since the last tick.  This method will remove itself from the task manager's event loop when the mouse
        button is released.

        Parameters
        ----------
        task: Task
              The Task parameter, used by the TaskManager.

        """
        if not self.mouseWatcherNode.hasMouse() or not self.mouseWatcherNode.is_button_down('mouse1'):
            self.adjust_pivot(self.update_sticker_map)
            return task.done

        position = self.mouseWatcherNode.getMouse()
        delta_x = position[0] - self.previous_click[0]
        delta_y = position[1] - self.previous_click[1]
        self.pivot.setHpr(self.pivot, (-delta_x * MyApp.rotation_speed, delta_y * MyApp.rotation_speed, 0))
        self.previous_click = (position[0], position[1])


        return task.cont

    def update_sticker_map(self):
        if self.pivot.getH() % 45 == 0 and abs(self.pivot.getP()) == 35 and self.pivot.getR() == 0:
            self.sticker_map = self._get_sticker_map()

    def move_to(self, angle, callback=lambda: None):
        """Gradually moves the pivot HPR until it is at the specified angles.  Optionally calls the specified
        callback when the movement is finished.

        Parameters
        ----------
        angle:  tuple of float
                The final rotation after the movement is complete.

        callback:  function
                   A callback function, called after the movement is complete.
        """

        move = LerpHprInterval(self.pivot, 0.2, Point3(angle[0], angle[1], angle[2]))
        sequence = Sequence(
                        move,
                        Func(callback),
        )
        sequence.start()

    def adjust_pivot(self, callback=lambda: None):
        """Moves the cube to the nearest fixed orientation and hides the hideable labels.  Optionally calls
        the specified callback when the movement is finished.

        Parameters
        ----------
        callback:  function
                   A callback function, called after the movement is complete.
        """
        self.hide_labels()
        self.move_to(Geometry.get_snapped_angles(self.pivot.getHpr()), callback)

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

    def _get_sticker_map(self):
        """Returns a map of each screen position id to the sticker that it maps to on the screen currently,
        where the id corresponds to an arbitrary ordering as follows:  When the top of the cube is visible
        (the pitch of the cube is -35), the 0 index is the sticker at the highest point on the screen.
        After that, the order proceeds down the cube layer by layer, from left to right.  Therefore, the
        indices 1, 2, and 3 are the other 3 stickers on the up face, from left to right.  4-7 are the
        stickers adjacent to stickers 1-3, but one layer down, again from left to right.  And 8-11 are the
        lowest stickers on the screen, from left to right.  When the bottom face is visible (pitch +35),
        the pattern is similar, except the 0 index is at the bottom, and it proceeds layer by layer upward,
        again from left to right."""

        angle = self.pivot.getHpr()
        sticker_map = {}
        left_axis = 0
        right_axis = 0
        if angle[0] == -45 or angle[0] == 135:
            right_axis = 1
        if angle[0] == 45 or angle[0] == -135:
            left_axis = 1
        if left_axis == right_axis:
            print(str(angle[0]))
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

            if wing_one[2][2] == wing_two[2][2]:
                if wing_one[2][left_axis] != sticker[2][left_axis]:
                    wing_one, wing_two = wing_two, wing_one
            else:
                if wing_one[2][2] != sticker[2][2]:
                    wing_one, wing_two = wing_two, wing_one

            # NOTE: sticker[0] refers to the point on the sticker that is in the middle of a face of the cube.

            if sticker[0][2] == corner[2]: # if the middle point on this sticker faces up
                sticker_map[2] = sticker
                sticker_map[0] = far_corner
                sticker_map[1] = wing_one
                sticker_map[3] = wing_two
            if sticker[0][left_axis] == corner[left_axis]:  # if the middle point on this sticker faces left
                sticker_map[5] = sticker
                sticker_map[8] = far_corner
                sticker_map[4] = wing_one
                sticker_map[9] = wing_two
            if sticker[0][right_axis] == corner[right_axis]:  # if the middle point on this sticker faces right
                sticker_map[6] = sticker
                sticker_map[11] = far_corner
                sticker_map[7] = wing_one
                sticker_map[10] = wing_two

        return sticker_map


app = MyApp()
app.run()
