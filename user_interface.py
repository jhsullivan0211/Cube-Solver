"""Contains the classes needed to build and run the GUI.

The GUI for this 2x2x2 cube solving application consists of a window, a 3D graphic representation of a 2x2x2 cube
which can be rotated by clicking and dragging the mouse, a selection for the color to apply to a sticker on click,
a solve button to start the solving algorithm, a label to display the solution, and various helper labels to clarify
the cube nomenclature and show the orientation of the cube.

This module contains the main GUI class "MainGUI", which draws all of the widgets and the cube onto a window using the
Panda3d graphics library.  Additionally, it contains a CubeModel class which contains the data of the cube, a
CubeController class to mediate between this module and the cube_logic.py module, and a Geometry utility class,
which contains special geometry functions that are specific to this model."""

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

        self.sticker_nodepath_map = {}
        self.stickers = CubeModel._generate_stickers()
        self.color_map = {sticker: CubeModel.blank_color for sticker in self.stickers}
        self.build_model()

    def build_model(self):
        """Builds and draws the node paths for the cube."""
        for sticker in self.stickers:
            geom_node = GeomNode('gnode')

            sticker_geom = self._build_sticker_geom(sticker, self.color_map[sticker], CubeModel.sticker_scale)
            geom_node.addGeom(sticker_geom)
            node_path = render.attachNewNode(geom_node)
            node_path.setTwoSided(True)
            self.sticker_nodepath_map[sticker] = node_path
            frame_sticker = tuple(Geometry.scale_vector(point, 0.99) for point in sticker)
            frame_node = GeomNode('framenode')
            frame_geom = self._build_sticker_geom(frame_sticker, CubeModel.back_color, 1)
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
        """Returns all of the stickers on the cube that contain the specified points.

        Parameters
        ----------
        *points: *int
                 A variable number of points, where the returned sticker contains each point listed.

        Returns
        -------
        tuple of stickers
            All stickers that contain the specified points.
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
    def _build_sticker_geom(sticker, sticker_color, scalar=1):
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

        Returns
        -------
        Geom
            The just-built Geom of the sticker.
        """

        sticker = CubeModel._scale_sticker(sticker, scalar)
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
    def _scale_sticker(sticker, scalar):
        """Given a sticker (tuple of 4 points), returns the same sticker, but scaled by the specified amount.
        NOTE: this is not quite scaling, since the only dimensions that change ard those parallel to the plane
        of the sticker.

        Parameters
        ---------
        sticker: tuple
                 A size-4 tuple consisting of the middle, edge, corner, and edge points, respectively.

        scalar:  The amount to scale the sticker quad.

        Returns
        -------
        tuple of tuple of float
            The scaled version of the same sticker.

        """
        result = []

        for i in range(len(sticker)):
            j = i + 2
            if j >= len(sticker):
                j -= len(sticker)

            # Get a vector that points across the sticker from this point, then scale it and return the point.
            movement = Geometry.subtract_vectors(sticker[j], sticker[i])
            movement = Geometry.scale_vector(movement, 1 - scalar)
            new_point = Geometry.add_vectors(sticker[i], movement)
            result.append(new_point)
        return tuple(result)

    @staticmethod
    def _generate_stickers():
        """Generates a tuple of 'stickers', each of which consists of four vertices in space in the following
        order: middle, edge, corner, edge.  Does not provide a guarantee of which edge point is which.

        Returns
        -------
        tuple of stickers
            A tuple containing all of the stickers generated.
        """

        stickers = []

        # From the center, use the branch() method to generate points in the middle of each face.  Then use
        # the branch() method on the middle points to generate edges points, and on the edge points to generate
        # corner points.  Doing this for all branches from the center ends up forming a tree, with leaf nodes at
        # the corner points and paths forming chains from middles to edges to corners.  Wherever two paths converge
        # on a single corner, the points of each path together form a sticker.

        middles = CubeModel._branch((0, 0, 0))
        for middle in middles:
            corner_to_edge = {}
            edges = CubeModel._branch(middle)
            for edge in edges:
                corners = CubeModel._branch(edge)
                for corner in corners:
                    if corner in corner_to_edge:
                        sticker = middle, edge, corner,  corner_to_edge[corner]
                        stickers.append(sticker)
                    else:
                        corner_to_edge[corner] = edge

        return tuple(stickers)

    @staticmethod
    def _branch(point):
        """Given a vertex on the cube, gets all points that can be reached by advancing (i.e. going to 1
        or -1 from 0) in a single axis direction.  This functions in such a way that by calling this
        on the center point of the cube it generates middle points, from a middle point it generates the
        four edge points on the same face, and from an edge point it generates the two adjacent corner points.

        Parameters
        ----------
        point:  tuple
                The point from which to branch.

        Returns
        -------
        list of point
            A list of points reachable by setting a single axis value from a 0 to 1 or -1.
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
              way around the axis.

        Returns
        -------
        float
            The snapped angle for heading.
        """

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
        """Returns the Euler rotation angles for heading (yaw), pitch, and roll where each is sngle is snapped, i.e. the
        rotation is forced to be angles of (45N, +-35, 0) where N is some integer.  The resulting rotation if used
        for the cube puts the cube in the proper orientation for clicking.

        Parameters
        ----------
        angles: iterable of angles
                A set of three angles corresponding to a (heading, pitch, roll) Euler rotation.

        Returns
        -------
        tuple of float
            The Euler rotation angles for heading (yaw), pitch, and roll, where each angle is snapped.
        """
        return Geometry.snap_h(angles[0]), -MainGUI.origin_rot[1] if angles[1] >= 0 else MainGUI.origin_rot[1], 0

    @staticmethod
    def get_distance(vector1, vector2):
        """Returns the distance (scalar) between two vectors.

        Parameters
        ----------
        vector1: tuple of float
                 The first vector.

        vector2: tuple of float
                 The second vector.

        Returns
        -------
        float
            The distance between the supplied vectors.
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

        Returns
        -------
        tuple of float
            The vector resulting from the subtraction.
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

        Returns
        -------
        tuple of float
            The vector resulting from the addition.
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

        Returns
        -------
        tuple of float
            The vector resulting from scaling the supplied vector.
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

        Returns
        -------
        bool
            True if the given point lies within the quad, False if not.
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

        Returns
        -------
        float
            The angle formed from points C, A, and B.

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

    @staticmethod
    def get_2d_point_in_direction(origin, direction, magnitude):
        """Given a 2D point of form (x, y), returns a new point that results from moving in the specified direction
        (i.e. angle where 0 = right) the specified amount.

        Parameters
        ----------
        origin: tuple of float
                The original 2D point, in the form (x, y).

        direction: float
                   The angle, in degrees.

        magnitude: float
                   The magnitude of the movement vector.

        Returns
        -------
        tuple of float
            The point resulting from the movement."""

        angle = math.radians(direction)
        return origin[0] + math.cos(angle) * magnitude, origin[1] + math.sin(angle) * magnitude

    @staticmethod
    def get_diamond(origin, angle, side_length):
        """Given a 2D origin point and an angle, returns a diamond with angles 120, 30, 120, and 30 degrees with the
        specified side length, such that the origin is at one of the 120-degree angle vertices.  The angle specifies
        the Euler rotation around the z-axis of the diamond in degrees.  At 0 degrees, the origin is the left vertex
        of the diamond.  Returns the points in clockwise order starting at the origin.

        Parameters
        ----------
        origin: tuple of float
            The 2D origin point in the form (x, y).
        angle: float
            The angle describing the rotation around the z-axis of the diamond, in degrees.
        side_length: float
            The side length.

        Returns
        -------
        tuple of tuple of float
            A collection of 4 points, where a point is of the form (x, y).  The 4 points are in clockwise order
            starting from the origin.
        """

        point_b = Geometry.get_2d_point_in_direction(origin, angle + 60, side_length)
        point_c = Geometry.get_2d_point_in_direction(point_b, angle - 60, side_length)
        point_d = Geometry.get_2d_point_in_direction(point_c, angle - 120, side_length)

        return origin, point_b, point_c, point_d


class CubeController:
    """A mediator between the GUI of this module (specifically the CubeModel class) and the cube_logic module which
    has the capability to build and solve the logical cube."""

    _already_solved_message = "Cube is already solved."
    _unsolvable_message = "This cube is impossible to solve."

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
        the cube is unsolvable or it is already solved.

        Returns
        -------
        str
            The solution, formatted for the UI, or the appropriate message upon failure.
        """

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


class MainGUI(ShowBase):
    """Runs the GUI, which displays the cube, a selection for color, a solve button, a lebel for the solution,
    and various helpful labels for interpreting the results correctly."""

    rotation_speed = 120
    mouse_speed_factor = 1
    screen_sticker_edge = 0.272
    origin_rot = (-45, -35, 0)

    def __init__(self):
        """Basic constructor for MyApp."""
        ShowBase.__init__(self)

        self.disableMouse()
        self.camera.setPos(0, -10, 0)
        properties = WindowProperties()
        properties.setTitle("2x2x2 Cube Solver")
        self.win.requestProperties(properties)
        self.cube = CubeModel()
        self.pivot = render.attachNewNode("pivot")
        self.pivot.setPos((0, 0, 0))
        self.camera.wrtReparentTo(self.pivot)
        self.pivot.setHpr(MainGUI.origin_rot)
        self.moving = False
        self._add_widgets()
        self.sticker_map = {}
        self.move_to(MainGUI.origin_rot, self.update_sticker_map)
        self.accept('mouse1', self.mouse_click)
        self.previous_click = None
        self.taskMgr.add(self._lock_format, "format lock")
        self.face_up_zones = MainGUI.build_zones(90)
        self.face_down_zones = MainGUI.build_zones(-90)
        self.debug_mark((1, .99))


    def debug_mark(self, position):
        self.mark = DirectLabel(text=".",
                                scale=0.1,
                                pos=(position[0] * 8/6, 0, position[1]),
                                frameColor=self.getBackgroundColor())
        print(position)


    def _add_widgets(self):
        """Adds the widgets to the window."""


        self.solve_button = DirectButton(text="Solve!",
                                         command=self._solve_setup,
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

        self._hide_labels()

    def _lock_format(self, task):
        """Forces the window to remain the same size.  Called every tick.

        Returns
        -------
        task function
            Returns a 'continue' message to the task manager running this task, each tick."""

        if self.win.getXSize() != 800 or self.win.getYSize() != 600:
            wp = WindowProperties()
            wp.setSize(800, 600)
            self.win.requestProperties(wp)
        return task.cont

    def _solve_setup(self):
        self.solution_label["text"] = "Thinking..."
        self.move_to(MainGUI.origin_rot, self.solve_cube)

    def _hide_labels(self):
        """Hides the labels that may be hidden."""

        self.left_label.hide()
        self.up_label.hide()
        self.front_label.hide()
        self.case_label.hide()
        self.solution_label["text"] = ""

    def _show_labels(self):
        """Shows the labels that may be hidden."""

        self.left_label.show()
        self.front_label.show()
        self.up_label.show()
        self.case_label.show()

    def solve_cube(self):
        """Solves the cube currently drawn on the graphical cube model for this application."""
        self.solution_label["text"] = "Thinking..."
        self.update_sticker_map()
        controller = CubeController(self.cube)
        solution = controller.solve()
        self.solution_label["text"] = solution
        self._show_labels()

    def mouse_click(self):
        """The method to perform when the left mouse button is clicked.  Creates a task that runs each tick
        while the mouse is clicked which updates the rotation of the cube by the position of the mouse, and
        also checks to see if a sticker is clicked when in its fixed position, coloring that sticker if it is
        with the color specified by the color selection widget of the GUI."""

        if self.mouseWatcherNode.hasMouse():
            position = self.mouseWatcherNode.getMouse()
            mouse_pos = (position.getX(), position.getY())

            zones = None
            if self.pivot.getP() == -35:
                zones = self.face_up_zones
            elif self.pivot.getP() == 35:
                zones = self.face_down_zones
            else:
                return
            clicked_sticker = False
            for i in range(len(zones)):
                zone = zones[i]
                if Geometry.is_within(mouse_pos, zone):
                    self.debug_mark(mouse_pos)
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

        Returns
        -------
        task function
            Returns the command for the task manager to either continue (call this again next tick) or finish
            and remove this from the task.

        """
        if not self.mouseWatcherNode.hasMouse() or not self.mouseWatcherNode.is_button_down('mouse1'):
            self.adjust_pivot(self.update_sticker_map)
            return task.done

        position = self.mouseWatcherNode.getMouse()
        delta_x = position[0] - self.previous_click[0]
        delta_y = position[1] - self.previous_click[1]
        self.pivot.setHpr(self.pivot, (-delta_x * MainGUI.rotation_speed, delta_y * MainGUI.rotation_speed, 0))
        self.previous_click = (position[0], position[1])

        return task.cont

    def update_sticker_map(self):
        """Updates the current sticker map if the cube is properly aligned."""
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
        self._hide_labels()
        self.move_to(Geometry.get_snapped_angles(self.pivot.getHpr()), callback)

    def get_nearest_corner(self):
        """Returns the corner nearest to the camera."

        Returns
        -------
        tuple of float
            An (x, y, z) point describing the corner nearest to the camera.  Uses Panda3d coordinates.
        """
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

    @staticmethod
    def build_zones(angle_offset):
        """Creates a tuple of 'zones', where a zone is just four points on the screen marking where a sticker
        is currently.  Note, these are 2D screen points, not 3D world vectors.  The order of these zones proceeds
        as follows:  Starting from the origin (0, 0) with the sticker touching the origin and on the Up face,
        proceed around the Up face clockwise, then move to the sticker touching the origin on the front face,
        again move around clockwise to each sticker on that face, then to the origin sticker on the left face,
        clockwise around, and then that is all of the zones.  The resulting tuple contains zones for all stickers
        currently visible.

        Parameters
        ----------
        angle: float
               The angle of all of the zones, in degrees.  Use 90 for when the top of the cube is visible, and
               -90 for when the bottom of the cube is visible.

        Returns
        -------
        tuple of tuple
            The zones of the screen, such that the """

        zones = []
        origin = (0, 0)
        for i in range(3):
            angle = -i * 120 + angle_offset
            inner_zone = Geometry.get_diamond(origin, angle, MainGUI.screen_sticker_edge)
            zones.append(inner_zone)
            for point in inner_zone[1:]:
                point_zone = Geometry.get_diamond(point, angle, MainGUI.screen_sticker_edge)
                zones.append(point_zone)

        return zones

    def _get_sticker_map(self):
        """Returns a map of each screen position id to the sticker that it maps to on the screen currently,
        where the id corresponds to an arbitrary ordering as follows:  When the top of the cube is visible
        (the pitch of the cube is -35), the 0 index is the sticker at the highest point on the screen.
        After that, the order proceeds down the cube layer by layer, from left to right.  Therefore, the
        indices 1, 2, and 3 are the other 3 stickers on the up face, from left to right.  4-7 are the
        stickers adjacent to stickers 1-3, but one layer down, again from left to right.  And 8-11 are the
        lowest stickers on the screen, from left to right.  When the bottom face is visible (pitch +35),
        the pattern is similar, except the 0 index is at the bottom, and it proceeds layer by layer upward,
        again from left to right.

        Returns
        -------
        dict of int: (tuple of tuple float)
            A map of integer IDs (see above for description) to stickers (a sticker is a tuple of four points).
        """

        angle = self.pivot.getHpr()
        sticker_map = {}

        # Determine which axis of the cube is facing which way (since the cube never really rotates, only the
        # camera). The 1 and 0 here represent indices of an (x, y, z) point according to the Panda3d coordinate
        # system.

        if angle[0] == -45 or angle[0] == 135:
            right_axis, left_axis = 1, 0
        elif angle[0] == 45 or angle[0] == -135:
            right_axis, left_axis = 0, 1
        else:
            raise Exception("Cube angle is not correct for generating the sticker map.")

        if angle[1] == 35:
            right_axis, left_axis = left_axis, right_axis

        # Get corner stickers, then for each of those stickers, get the other stickers on the same face
        corner = self.get_nearest_corner()
        corner_stickers = self.cube.get_stickers_with_points(corner)

        for sticker in corner_stickers:
            corner_point = sticker[2]
            mid_point = sticker[0]

            # The same vector going from the corner point to the mid point (i.e. point in the middle of a face),
            # if applied with the origin at the mid point, ends at the far corner point of the cube.

            corner_to_mid = Geometry.subtract_vectors(mid_point, corner_point)
            far_corner_point = Geometry.add_vectors(mid_point, corner_to_mid)
            far_corner = self.cube.get_stickers_with_points(mid_point, far_corner_point)[0] #index 0 = middle point.

            # 'Edges' refers to the remaining two stickers on this face, found by getting all stickers containing
            # the mid point and then removing the stickers we have already found

            edges = list(self.cube.get_stickers_with_points(mid_point))
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

            # Now all of the stickers on the given face (the face that the current sticker is located on) have been
            # found.  Each one now needs a specific ID corresponding to a pre-determined arbitrary order.  First
            # we determine which axis the sticker is pointing towards, then we attribute each sticker to its ID.

            if sticker[0][2] == corner[2]: # if the middle point on this sticker faces up
                sticker_map[0] = sticker
                sticker_map[2] = far_corner
                sticker_map[1] = wing_one
                sticker_map[3] = wing_two
            if sticker[0][left_axis] == corner[left_axis]:  # if the middle point on this sticker faces left
                sticker_map[8] = sticker
                sticker_map[10] = far_corner
                sticker_map[11] = wing_one
                sticker_map[9] = wing_two
            if sticker[0][right_axis] == corner[right_axis]:  # if the middle point on this sticker faces right
                sticker_map[4] = sticker
                sticker_map[6] = far_corner
                sticker_map[5] = wing_one
                sticker_map[7] = wing_two

        return sticker_map


app = MainGUI()
app.run()
