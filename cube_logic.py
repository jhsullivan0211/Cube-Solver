"""
Contains the logic for solving a 2x2x2 rubik's cube.

"""


class Cube:
    """Contains the data representation for the cube, as well as methods to perform each move."""
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

    def __init__(self, configuration):
        self.configuration = configuration

    def __hash__(self):
        return hash(self.configuration)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self.configuration == other.configuration

    def do_move(self, move):
        if move in Cube.move_dict:
            self.configuration = Cube.__permute(self.configuration, Cube.move_dict[move])
        else:
            raise ValueError("Unknown move \"" + move + "\" supplied.")

    def do_moves(self, moves):
        for move in moves:
            self.do_move(move)

    def is_solved(self):
        return self.configuration == Cube.solved_tuple

    @staticmethod
    def __permute(group, order):
        return tuple(group[i] for i in order)

    @staticmethod
    def new_cube():
        return Cube(Cube.solved_tuple)


test = Cube.new_cube()

test.do_moves("FRUrufBdLbDl")

assert(test.configuration == ('back', 'right', 'up', 'up', 'left', 'back', 'front', 'down', 'left',
                              'left', 'up', 'front', 'right', 'back', 'down', 'down', 'front', 'right', 'left',
                              'down', 'back', 'right', 'front', 'up'))

