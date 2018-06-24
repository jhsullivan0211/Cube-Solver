"""
Contains the logic for solving a 2x2x2 rubik's cube.

"""


class Cube:
    """
    A data structure for representing a cube, with its current state representing the state of the cube,
    i.e. the location of every sticker.  Contains methods to perform the different moves of the cube,
    which are just rotations of each face.  Also contains some utility methods that assist in solving
    the cube.
    """

    solved_tuple = ("up", "front", "left", "up", "left", "back", "up", "back", "right", "up", "right", "front",
                    "down", "left", "front", "down", "back", "left", "down", "right", "back", "down", "front", "right")

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
                       21, 22, 23, 12, 13, 14, 15, 16, 17, 18, 19, 20)}

    symbol_count = len(solved_tuple)

    maximum_moves = 14

    def __init__(self, configuration):
        """A basic constructor for the Cube class."""
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
        """Cubes with matching configurations are considered equal."""
        return self.__class__ == other.__class__ and \
               self.configuration == other.configuration

    def do_move(self, move):
        """Performs the specified move on the cube."""
        if move in Cube.move_dict:
            self.configuration = Cube.__permute(self.configuration, Cube.move_dict[move])
        else:
            raise ValueError("Unknown move \"" + move + "\" supplied.")

    def do_moves(self, moves):
        """Performs the specified moves on the cube."""
        for move in moves:
            self.do_move(move)

    def set_marker(self, marker):
        """Sets the 'marker' field, which denotes which move produced the current state."""
        self.marker = marker

    @staticmethod
    def new_cube():
        """Returns a new Cube with a solved configuration."""
        return Cube(Cube.solved_tuple)

    @staticmethod
    def invert_move(move_str):
        """Given a move, returns its inverse."""
        if move_str.islower():
            return move_str.upper()
        else:
            return move_str.lower()

    @staticmethod
    def __permute(group, order):
        """Permutes the specified group by setting the index of each element
        to the corresponding index specified in the order argument."""
        return tuple(group[i] for i in order)


class Searcher:
    """A class which offers up elements according to breadth-first traversal using a cube's implicit graph."""

    def __init__(self, start, search_moves=None):
        """A basic constructor for the Searcher class."""
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
        Defaults to doing all possible moves if no search moves are specified."""
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


class Solver:
    """A class containing static methods for solving a given cube.  Use Solver.get_solution to solve a
    cube; the other methods are meant to be internal."""

    @staticmethod
    def find_target(origin, target, search_moves=None):
        """Performs two-way breadth-first search to find a pair of matching cube states,
        one reached by starting the search at the front (i.e. unsolved) state and one reached
        by starting at the back (i.e. solved) state, meeting in the middle somewhere.  These c
        ube configurations are the same, but have different parent chains, so following both
        chains will lead to the front and back of the search.  Returns the pair as a pair like
        so: (front-found, back-found)."""

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
    def get_parent_chain(target):
        """Returns a list representing the chain of parents from the specified cube until the root."""
        chain = []
        current_parent = target

        while current_parent is not None:
            chain.append(current_parent)
            current_parent = current_parent.parent

        return chain

    @staticmethod
    def get_solution(origin, target, moves="URLFBDurlfbd"):
        """Returns a string of moves that will get one from the specified origin state to the specified
        target state, using only the specified moves."""

        solved_set = Solver.find_target(origin, target, moves)

        if solved_set is None:
            raise ValueError("Cube is unsolvable.")

        front = solved_set[0]
        back = solved_set[1]
        front_chain = Solver.get_parent_chain(front)
        back_chain = Solver.get_parent_chain(back)

        solution = []
        for link in reversed(front_chain):
            if link.marker is not None:
                solution += link.marker

        for link in back_chain:
            if link.marker is not None:
                solution += Cube.invert_move(link.marker)

        return solution


test_cube = Cube.new_cube()
test_cube.do_moves("RUFururDbuR")
solution = Solver.get_solution(test_cube, Cube.new_cube())
print(solution)
