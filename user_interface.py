"""Contains the classes needed to build and run the UI."""
import pygame
import random
from pygame.locals import *
import math

from OpenGL.GL import *
from OpenGL.GLU import *


class CubeDrawer:
    """Contains data and methods for drawing a cube."""
    stickers = None
    color_map = {}

    def __init__(self):
        """Constructor for CubeDrawer.  Generates all of the points of the cube and stores them
        for quick drawing, as well as a map of each sticker to its proper color.  NOTE: the name
        'sticker' here may be somewhat misleading, because it is actually the entire square space
        around and including the sticker on a real cube."""

        self.stickers = CubeDrawer.generate_stickers()
        for sticker in self.stickers:
            red = random.random()
            green = random.random()
            blue = random.random()
            self.color_map[sticker] = tuple([red, green, blue])
            print(self.color_map)


    def draw_cube(self):
        """Draws the cube using the stickers built during construction."""
        for sticker in self.stickers:
            self.draw_sticker(sticker, self.color_map[sticker])

    @staticmethod
    def draw_sticker(sticker, sticker_color):
        """Draws a single sticker the specified sticker color."""
        glBegin(GL_TRIANGLES)

        glColor(sticker_color)
        glVertex(sticker[0])
        glVertex(sticker[2])
        glVertex(sticker[3])

        glVertex(sticker[1])
        glVertex(sticker[2])
        glVertex(sticker[3])

        # glColor(255, 0, 0)
        # glVertex(colored_part[0])
        # glVertex(colored_part[2])
        # glVertex(colored_part[3])
        #
        # glVertex(colored_part[1])
        # glVertex(colored_part[2])
        # glVertex(colored_part[3])

        glEnd()

    @staticmethod
    def scale_square(square, scalar):
        """Returns a square scaled by the specified scalar such that the center remains the same."""
        result = []
        for point in square:
            scaled = []
            for component in point:
                scaled_val = component * scalar
                scaled.append(scaled_val)
            result.append(tuple(scaled))
        return tuple(result)


    @staticmethod
    def generate_stickers():
        """Generates a tuple of 'stickers', each of which consists of four vertices in space in the following
        order: middle, corner, edge1, edge2."""

        stickers = []
        edge_to_mid = {}
        middles = CubeDrawer.branch((0, 0, 0))

        for middle in middles:
            corner_to_edge = {}
            edges = CubeDrawer.branch(middle)
            for edge in edges:
                edge_to_mid[edge] = middle
                corners = CubeDrawer.branch(edge)
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
        away from zero) in a single axis direction.  This functions in such a way that, by calling this
        on the center point, it generates middle points; from middle points, it generates edge points;
        and from edge points, it generates corner points."""

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


def main():
    """The main entry to the program, which loads the GUI and runs the main loop."""

    # Initialization
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    glEnable(GL_DEPTH_TEST)

    drawer = CubeDrawer()
    rotate_x = False
    rotate_y = False
    x_angle = 0
    y_angle = 0
    z_angle = 0

    # Main loop, executed every tick:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    rotate_y = True
                if event.button == 3:
                    rotate_x = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    rotate_y = False
                if event.button == 3:
                    rotate_x = False

        message = ""

        if rotate_x:
            # x_factor = math.cos(math.radians(y_angle))
            # y_factor = math.sin(math.radians(z_angle))
            # z_factor = math.sin(math.radians(y_angle))

            x_factor = 1
            y_factor = 0
            z_factor = 0

            glRotate(1, x_factor, y_factor, z_factor)

            x_angle += x_factor
            y_angle += y_factor
            z_angle += z_factor

            if x_angle == 360:
                x_angle = 0
            #print(str(x_angle) + ", " + str(y_angle))

        if rotate_y:
            # x_factor = math.sin(math.radians(z_angle))
            # y_factor = math.cos(math.radians(x_angle))
            # z_factor = math.sin(math.radians(x_angle))

            x_factor = 0
            y_factor = 1
            z_factor = 1

            glRotate(1, x_factor, y_factor, z_factor)

            x_angle += x_factor
            y_angle += y_factor
            z_angle += z_factor

            if y_angle == 360:
                y_angle = 0
            #print(str(x_angle) + ", " + str(y_angle) + ", " + str(z_angle))

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        drawer.draw_cube()
        pygame.display.flip()
        pygame.time.wait(10)


main()