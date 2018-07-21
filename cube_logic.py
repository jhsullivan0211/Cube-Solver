"""  Contains the 2x2x2 Pocket Cube logic portion of the application.

Contains the data representation (i.e. the location of each sticker) of the cube,
as well as the algorithms representing the different possible moves of the cube.
Additionally, contains algorithms to solve the cube optimally (i.e. the shortest
number moves) using a two-way variant of breadth-first search.  The cube is
represented as a length-24 array of direction labels (e.g. "up", "left", etc.), where each
label represents the color that would be found in the solved cube on the face in that
particular direction.  The solved cube would have all of the "up" labels at indices
that correspond to the upper face of the cube, all the "left" on the left face, and so forth.

One difficulty with this approach is that a solved cube can be oriented many different ways
in space, which would correspond to a different solved array under the current data structure.
This would complicate the search algorithm, since there would then be twenty-four potential
solutions to search for, any of which could be nearest. To remedy this, one corner piece is
assumed to already be in the correct position, and the cube is solved under this assumption,
without moving this corner.  This can be done because, for a 2x2x2 cube, turning any one face
is the same as turning the opposite face the same direction (e.g. a clockwise turn of the
right face is the same as a clockwise turn of the left face), if you view each piece's location
only in terms of its relation to other pieces. By leaving the chosen corner in place, this
fixes the solved state to be a single orientation.  An additional benefit of this is that,
because no moves that displace the fixed piece are allowed, the branching factor of the
cube's implicit graph is reduced from 12 to 6, which speeds up the algorithm considerably
without missing any potential solutions.

The sticker-to-index mapping was chosen arbitrarily, and is listed below using a
notation that works as follows:  A sticker is described using a three-letter triplet,
e.g. URF.  The first letter designates the face of the cube (where U = the upper
face (pointing at the ceiling), F = the front (pointing at the holder), R = right,
L = left, B = back, and D = down/bottom).  The second and third letters serve to
further identify the sticker location.  For example, URF would represent the sticker
facing up, in the right half of the cube toward the front side.  The following shows the
mapping of sticker positions to indexes:

{0=ULF, 1=ULB, 2=URB, 3=URF, 4=FUL, 5=LUF, 6=LUB, 7=BLU, 8=BRU, 9=RUB, 10=RUF, 11=FUR, 12=FDL,
13=LDF, 14=LDB, 15=BDL, 16=BDR, 17=RDB, 18=RDF, 19=FDR, 20=DFL, 21=DBL, 22 = DBR, 23=DFR}"""

import time
import random

class Cube:
    """
    A data structure for representing a cube, with its current state representing the state of the cube,
    i.e. the location of every sticker.  Contains methods to perform the different moves of the cube,
    which are just rotations of each face.  Also contains some utility methods that assist in solving
    the cube.
    """

    up_symbol = "up"
    front_symbol = "front"
    left_symbol = "left"
    right_symbol = "right"
    back_symbol = "back"
    down_symbol = "down"
    symbol_set = (up_symbol, front_symbol, left_symbol, right_symbol, back_symbol, down_symbol)

    solved_tuple = (up_symbol, front_symbol, left_symbol, up_symbol, left_symbol, back_symbol, up_symbol, back_symbol,
                    right_symbol, up_symbol, right_symbol, front_symbol, down_symbol, left_symbol, front_symbol,
                    down_symbol, back_symbol, left_symbol, down_symbol, right_symbol, back_symbol,
                    down_symbol, front_symbol, right_symbol)

    cubies = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14), (15, 16, 17), (18, 19, 20), (21, 22, 23))

    move_dict = {"U": (9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8,
                       12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23),
                 "R": (0, 1, 2, 3, 4, 5, 11, 9, 10, 22, 23, 21,
                       12, 13, 14, 15, 16, 17, 7, 8, 6, 20, 18, 19),
                 "L": (5, 3, 4, 16, 17, 15, 6, 7, 8, 9, 10, 11,
                       1, 2, 0, 14, 12, 13, 18, 19, 20, 21, 22, 23),
                 "F": (13, 14, 12, 3, 4, 5, 6, 7, 8, 2, 0, 1,
                       23, 21, 22, 15, 16, 17, 18, 19, 20, 10, 11, 9),
                 "B": (0, 1, 2, 8, 6, 7, 19, 20, 18, 9, 10, 11,
                       12, 13, 14, 4, 5, 3, 17, 15, 16, 21, 22, 23),
                 "D": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                       15, 16, 17, 18, 19, 20, 21, 22, 23, 12, 13, 14),
                 "u": (3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2,
                       12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23),
                 "r": (0, 1, 2, 3, 4, 5, 20, 18, 19, 7, 8, 6,
                       12, 13, 14, 15, 16, 17, 22, 23, 21, 11, 9, 10),
                 "l": (14, 12, 13, 1, 2, 0, 6, 7, 8, 9, 10, 11,
                       16, 17, 15, 5, 3, 4, 18, 19, 20, 21, 22, 23),
                 "f": (10, 11, 9, 3, 4, 5, 6, 7, 8, 23, 21, 22,
                       2, 0, 1, 15, 16, 17, 18, 19, 20, 13, 14, 12),
                 "b": (0, 1, 2, 17, 15, 16, 4, 5, 3, 9, 10, 11,
                       12, 13, 14, 19, 20, 18, 8, 6, 7, 21, 22, 23),
                 "d": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                       21, 22, 23, 12, 13, 14, 15, 16, 17, 18, 19, 20),
                 "R2": (0, 1, 2, 3, 4, 5, 21, 22, 23, 18, 19, 20,
                        12, 13, 14, 15, 16, 17, 9, 10, 11, 6, 7, 8),
                 "U2": (6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5,
                        12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23),
                 "L2": (15, 16, 17, 12, 13, 14, 6, 7, 8, 9, 10, 11,
                        3, 4, 5, 0, 1, 2, 18, 19, 20, 21, 22, 23),
                 "F2": (21, 22, 23, 3, 4, 5, 6, 7, 8, 12, 13, 14,
                        9, 10, 11, 15, 16, 17, 18, 19, 20, 0, 1, 2),
                 "B2": (0, 1, 2, 18, 19, 20, 15, 16, 17, 9, 10, 11,
                        12, 13, 14, 6, 7, 8, 3, 4, 5, 21, 22, 23),
                 "D2": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                        18, 19, 20, 21, 22, 23, 12, 13, 14, 15, 16, 17)}

    symbol_count = len(solved_tuple)

    maximum_moves = 14

    def __init__(self, configuration):
        """A basic constructor for the Cube class.

        Parameters
        ----------
        configuration : tuple
                        A tuple of symbols representing the direction a sticker points in the solved state.  For
                        example, if the symbol at a specific index (i.e. position on the cube) matches
                        Cube.front_symbol, then when solved that sticker should be on the front of the cube.

        """
        if len(configuration) != 24:
            raise ValueError("Must use a tuple of size 24.")
        self.configuration = configuration
        self.marker = ""
        self.parent = None
        self.orienting_moves = []

    def __hash__(self):
        """Cubes with matching configurations hash the same way."""
        return hash(self.configuration)

    def __eq__(self, other):
        """Cubes with matching configurations are considered equal.

        Parameters
        ----------
        other : Cube
                The cube to which to check equivalence.
        """
        return self.__class__ == other.__class__ and \
               self.configuration == other.configuration

    def do_move(self, move):
        """Performs the specified move on the cube.

        Parameters
        ----------
        move :  str
                The symbol defining the move.  Possible move strings are found as keys in Cube.move_dict, and
                currently contain the following:  "U", "u", "R", "r", "D", "d", "L", "l", "F", "f", "B", "b".
                Uppercase moves denote clockwise turns, lowercase denote counterclockwise turns.
        """
        if move in Cube.move_dict:
            self.configuration = Cube.__permute(self.configuration, Cube.move_dict[move])
        else:
            raise ValueError("Unknown move \"" + move + "\" supplied.")

    def do_moves(self, moves):
        """Performs the specified moves on the cube.

        Parameters
        ----------
        moves :  iterable<str>
                An iterable of symbols defining the moves to be performed.  Possible move strings are found as keys in
                Cube.move_dict, and currently contain the following:  "U", "u", "R", "r", "D", "d", "L", "l", "F", "f",
                 "B", "b".  Uppercase moves denote clockwise turns, lowercase denote counterclockwise turns."""

        for move in moves:
            self.do_move(move)

    def set_marker(self, marker):
        """Sets the 'marker' field, which denotes which move produced the current state.
        
        Parameters
        ----------
        marker : str
                 The value to which to set self.marker.
        """
        
        self.marker = marker

    @staticmethod
    def new_cube():
        """Returns a new Cube with a solved configuration."""
        return Cube(Cube.solved_tuple)

    @staticmethod
    def invert_move(move_str):
        """Given a move, returns its inverse.

        Parameters
        ----------
        move_str :  str
                    The move to invert.
        """
        if len(move_str) == 2:
            return move_str
        if move_str.islower():
            return move_str.upper()
        else:
            return move_str.lower()

    @staticmethod
    def __permute(group, order):
        """Permutes the specified group by setting the index of each element
        to the corresponding index specified in the order argument.

        Parameters
        ----------
        group : iterable<str>
                A collection of strings, which will be permuted.

        order : tuple
                An ordered collection of indices, which represent the resulting indices of the members of group.

        """
        return tuple(group[i] for i in order)


class Searcher:
    """A class which offers up elements according to breadth-first traversal using a cube's implicit graph."""

    def __init__(self, start, search_moves=None):
        """A basic constructor for the Searcher class.

        Parameters
        ----------
        start : Cube
                The starting Cube configuration.

        search_moves : collection<str>
                       A collection of moves to try when performing breadth-first search.
        """

        self.currentLayer = [start]
        self.nextLayer = []
        self.visited = {}
        self.count = 0
        self.layerNumber = 0
        self.search_moves = search_moves

    def get_next(self):
        """Returns the next element according to breadth-first traversal"""
        if self.count >= len(self.currentLayer):
            self.currentLayer = self.nextLayer
            self.nextLayer = []
            self.count = 0
            self.layerNumber += 1
        if len(self.currentLayer) == 0:
            return None

        current = self.currentLayer[self.count]
        if current.configuration in self.visited:
            self.count += 1
            return self.get_next()

        for child in Searcher.get_cube_children(current, self.search_moves):
            self.nextLayer.append(child)

        self.visited[current.configuration] = current
        self.count += 1
        return current

    @staticmethod
    def get_cube_children(cube, search_moves=None):
        """Gets the children of the cube, where children here means all of the
        cube states reachable by doing one of the moves specified in the search_moves
        argument.  Sets the marker of the discovered child to be the move that produced it,
        and sets the parent of the discovered child to be the parent that produced it.
        Defaults to doing all possible moves if no search moves are specified.

        Parameters
        ----------
        cube : Cube
                The cube from which to get the children.

        search_moves :  collection<str>
                        A collection of moves to perform to create children.
        """
        result = []
        if search_moves is None:
            search_moves = Cube.move_dict
        for key in search_moves:
            cube_child = Cube(cube.configuration)
            cube_child.do_move(key)
            cube_child.set_marker(key)
            cube_child.parent = cube
            result.append(cube_child)
        return result

    def get_visited(self):
        """Returns the collection of visited states."""
        return self.visited


class CubeBuilder:
    """Contains static methods for building a cube from a set of 24 colors.  The only method that
    should be called is get_cube_form_colors, which takes the UFR cube and treats it as if it were
    already solved, determining the rest of the colors' solved locations from that one.  Cubes built
    this way should be solved using only back, down, and right face turns."""

    solve_moves = ["R", "r", "F", "f", "U", "u"]

    @staticmethod
    def get_cube_from_colors(colors):
        """Returns a cube built using the specified colors, where the UFR cube is considered already
        solved and the rest of the colors assigned using that assumption.

        Parameters
        ----------
        colors :    iterable<str>
                    An ordered collection of symbols, to be formed into a Cube configuration.
        """
        symbol_dict = CubeBuilder.__get_symbols(colors)

        translate_list = []
        for color in colors:
            if color not in symbol_dict:
                raise ValueError("Error reading cube symbol " + color + ".")
            translate_list.append(symbol_dict[color])
        cube = Cube(tuple(translate_list))
        if CubeBuilder.__check_validity(cube):
            return cube
        else:
            raise ValueError("Invalid cube provided.")

    @staticmethod
    def __get_symbols(colors):
        """Returns a mapping of colors from the specified list to direction strings (e.g. "up", "right", etc.),
        which match the strings used in the configurations of the Cube class.

        Parameters
        ----------
        colors : iterable<str>
                 An ordered collection of symbols, to be mapped onto cube directions (e.g. "up", "front", etc.)
        """

        down_symbol = colors[15]
        back_symbol = colors[16]
        left_symbol = colors[17]
        up_symbol = None
        right_symbol = None
        front_symbol = None

        i = 0
        j = 3

        while j <= 24:
            if i == 15:
                i += 3
                j += 3
                continue

            triplet = colors[i:j]
            if up_symbol is None:
                up_symbol = CubeBuilder.__get_third(triplet, left_symbol, back_symbol)

            if right_symbol is None:
                right_symbol = CubeBuilder.__get_third(triplet, down_symbol, back_symbol)

            if front_symbol is None:
                front_symbol = CubeBuilder.__get_third(triplet, down_symbol, left_symbol)

            i += 3
            j += 3

        symbols = {up_symbol: Cube.up_symbol,
                   right_symbol: Cube.right_symbol,
                   left_symbol: Cube.left_symbol,
                   front_symbol: Cube.front_symbol,
                   back_symbol: Cube.back_symbol,
                   down_symbol: Cube.down_symbol}


        for symbol in symbols:
            if symbol is None:
                raise ValueError("Symbol map does not resolve correctly.")

        return symbols

    @staticmethod
    def __get_third(triplet, first, second):
        """Given a collection of three things and the first thing and second thing, returns the third thing
        in the collection.

        Parameters
        ----------
        triplet :   iterable
                    An iterable of size 3 containing the following two arguments, as well as a third.

        first :     object
                    The first object, found in the triplet parameter and so not returned.

        second :    ohject
                    The second object, found in the triplet parameter and so not returned.
        """
        if first in triplet and second in triplet:
            for thing in triplet:
                if thing != first and thing != second:
                    return thing
        return None

    @staticmethod
    def __check_validity(cube):
        """Checks the validity of a cube in advance to prevent exhaustively searching the entire search space.

        Parameters
        ----------
        cube :  Cube
                The Cube for which to check the validity."""

        color_map = {}
        for color in cube.configuration:
            color_map[color] = 0
        if len(color_map) != 6:
            return False
        for color in cube.configuration:
            color_map[color] += 1
        for color in color_map:
            if color_map[color] != 4:
                return False

        test_cube = []
        for i in range(0, len(cube.configuration), 3):
            triplet = (cube.configuration[i], cube.configuration[i + 1], cube.configuration[i + 2])

            for j in range(0, len(cube.configuration), 3):
                potential = (Cube.solved_tuple[j], Cube.solved_tuple[j + 1], Cube.solved_tuple[j + 2])
                if CubeBuilder.__check_triplet(triplet, potential):
                    test_cube.extend(triplet)
        test_cube = tuple(test_cube)
        if test_cube != cube.configuration:
            return False

        return True

    @staticmethod
    def __check_triplet(triplet, oriented_triplet):
        """Checks whether the specified triplet is a rotated version of the oriented triplet.

        Parameters
        ----------
        triplet :           iterable
                            The actual values of a given cubie.
        oriented_triplet :  iterable
                            The oriented value of the cubie, to be checked against.
        """
        if triplet[0] == oriented_triplet[0]:
            return triplet[1] == oriented_triplet[1] and triplet[2] == oriented_triplet[2]
        elif triplet[0] == oriented_triplet[1]:
            return triplet[1] == oriented_triplet[2] and triplet[2] == oriented_triplet[0]
        elif triplet[0] == oriented_triplet[2]:
            return triplet[1] == oriented_triplet[0] and triplet[2] == oriented_triplet[1]
        return False


class Solver:
    """A class containing static methods for solving a given cube.  Use Solver.get_solution to solve a
    cube; the other methods are meant to be internal."""

    @staticmethod
    def get_solution(origin, target, moves=CubeBuilder.solve_moves):
        """Given two cubes, returns a string of moves that will get one from the origin cube to the target cube,
        using only the specified moves.

        Parameters
        ----------
        origin : Cube
                 The Cube representing the starting state.
        target : Cube
                 The cube representin typically representing the solved state.
        moves : iterable<str>
                An ordered collection of moves which represent the possible moves to do.  Defaults to
                the moves specified by CubeBuilder.solve_moves, a restricted set of moves to optimize the
                search algorithm.
        """

        optimized_cube = CubeBuilder.get_cube_from_colors(origin.configuration)
        solved_set = Solver.__find_target(optimized_cube, target, moves)

        if solved_set is None:
            raise ValueError("CubeError: Cube is unsolvable.")

        front = solved_set[0]
        back = solved_set[1]
        front_chain = Solver.__get_parent_chain(front)
        back_chain = Solver.__get_parent_chain(back)

        solution = []
        for link in reversed(front_chain):
            if link.marker != "":
                solution.append(link.marker)

        for link in back_chain:
            if link.marker != "":
                solution.append(Cube.invert_move(link.marker))

        return solution

    @staticmethod
    def __find_target(origin, target, search_moves=None):
        """Performs two-way breadth-first search to find a pair of matching cube states,
        one reached by starting the search at the front (i.e. unsolved) state and one reached
        by starting at the back (i.e. solved) state, meeting in the middle somewhere.  These c
        ube configurations are the same, but have different parent chains, so following both
        chains will lead to the front and back of the search.  Returns the pair as a pair like
        so: (front-found, back-found).

        Parameters
        ----------
        origin : Cube
                 The Cube representing the starting state.
        target : Cube
                 The cube representin typically representing the solved state.
        moves : iterable<str>
                An ordered collection of moves which represent the possible moves to do.  Defaults to
                the moves specified by CubeBuilder.solve_moves, a restricted set of moves to optimize the
                search algorithm.
        """

        front_searcher = Searcher(origin, search_moves)
        back_searcher = Searcher(target, search_moves)

        current_front = front_searcher.get_next()
        current_back = back_searcher.get_next()

        failed = False
        while current_front is not None and current_back is not None:

            if current_front.configuration in back_searcher.visited:
                return [current_front, back_searcher.visited[current_front.configuration]]
            if current_back.configuration in front_searcher.visited:
                return [front_searcher.visited[current_back.configuration], current_back]

            current_front = front_searcher.get_next()
            current_back = back_searcher.get_next()

            if front_searcher.layerNumber + back_searcher.layerNumber > Cube.maximum_moves:
                failed = True
                break

        if failed:
            raise ValueError("Cube Error: cube is impossible to solve.")

        return None

    @staticmethod
    def __get_parent_chain(target):
        """Returns a list representing the chain of parents from the specified cube until the root.

        Parameters
        ----------
        target : Cube
                 The Cube from which to build the parent chain.
        """
        chain = []
        current_parent = target

        while current_parent is not None:
            chain.append(current_parent)
            current_parent = current_parent.parent

        return chain

