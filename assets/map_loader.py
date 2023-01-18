# Handles map requests and returns appropriate directory path to parent file

# Vertical checkpoint: [x, y, 32, 183]
# Horizontal checkpoint: [x, y, 215, 53]


class Racetrack:
    def __init__(self):
        self.name = 'racetrack'
        self._file_dir = 'assets/maps/racetrack/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'

    def layer(self, layer: int):
        """
        Returns a layer of the Racetrack track
        0 = Background (img)
        1 = Objects (img)
        2 = Track (img)
        3 = Checkpoints (2d array / tuples)
        """
        if layer == 0:
            return self._file_dir + self._bg
        elif layer == 1:
            return self._file_dir + self._obj
        elif layer == 2:
            return self._file_dir + self._trk
        elif layer == 3:
            return ((1312, 233, 32, 183), (1428, 513, 215, 53), (1376, 665, 32, 183), (928, 665, 32, 183),
                    (512, 665, 32, 183), (276, 513, 215, 53), (512, 233, 32, 183), (928, 233, 32, 183))
        else:
            raise ValueError("Racetrack.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    @staticmethod
    def start_pos(pos: int):
        """
        Returns the start position and rotation for each position on Racetrack (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return 1235, 285, 270
        elif pos == 2:
            return 1235, 355, 270
        elif pos == 3:
            return 1120, 285, 270
        elif pos == 4:
            return 1120, 355, 270
        elif pos == 5:
            return 1005, 285, 270
        elif pos == 6:
            return 1005, 355, 270
        else:
            raise ValueError("Racetrack.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class Snake:
    def __init__(self):
        self.name = 'snake'
        self._file_dir = 'assets/maps/snake/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'

    def layer(self, layer: int):
        """
        Returns a layer of the Snake track
        0 = Background (img)
        1 = Objects (img)
        2 = Track (img)
        3 = Checkpoints (2d array / tuples)
        """
        if layer == 0:
            return self._file_dir + self._bg
        elif layer == 1:
            return self._file_dir + self._obj
        elif layer == 2:
            return self._file_dir + self._trk
        elif layer == 3:
            return ((930, 773, 32, 183), (1172, 675, 216, 54), (1472, 449, 32, 183), (1556, 351, 216, 54),
                    (1376, 125, 32, 183), (928, 125, 32, 183), (660, 351, 216, 54), (480, 449, 32, 183),
                    (148, 675, 216, 54), (544, 773, 32, 183))
        else:
            raise ValueError("Snake.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    @staticmethod
    def start_pos(pos: int):
        """
        Returns the start position and rotation for each position on Snake (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return 853, 825, 270
        elif pos == 2:
            return 853, 895, 270
        elif pos == 3:
            return 738, 825, 270
        elif pos == 4:
            return 738, 895, 270
        elif pos == 5:
            return 623, 825, 270
        elif pos == 6:
            return 623, 895, 270
        else:
            raise ValueError("Snake.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class DogBone:
    def __init__(self):
        self.name = 'dog bone'
        self._file_dir = 'assets/maps/dog_bone/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'

    def layer(self, layer: int):
        """
        Returns a layer of the DogBone track
        0 = Background (img)
        1 = Objects (img)
        2 = Track (img)
        3 = Checkpoints (2d array / tuples)
        """
        if layer == 0:
            return self._file_dir + self._bg
        elif layer == 1:
            return self._file_dir + self._obj
        elif layer == 2:
            return self._file_dir + self._trk
        elif layer == 3:
            return ((576, 341, 32, 183), (148, 567, 216, 54), (448, 773, 31, 183), (768, 665, 32, 183),
                    (1120, 665, 32, 183), (1440, 773, 32, 183), (1556, 675, 216, 54),
                    (1556, 432, 216, 54), (1521, 125, 31, 183), (1184, 341, 31, 183))
        else:
            raise ValueError("DogBone.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    @staticmethod
    def start_pos(pos: int):
        """
        Returns the start position and rotation for each position on DogBone (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return 685, 393, 90
        elif pos == 2:
            return 685, 463, 90
        elif pos == 3:
            return 800, 393, 90
        elif pos == 4:
            return 800, 463, 90
        elif pos == 5:
            return 915, 393, 90
        elif pos == 6:
            return 915, 463, 90
        else:
            raise ValueError("DogBone.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class Hairpin:
    def __init__(self):
        self.name = 'hairpin'
        self._file_dir = 'assets/maps/hairpin/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'

    def layer(self, layer: int):
        """
        Returns a layer of the Hairpin track
        0 = Background (img)
        1 = Objects (img)
        2 = Track (img)
        3 = Checkpoints (2d array / tuples)
        """
        if layer == 0:
            return self._file_dir + self._bg
        elif layer == 1:
            return self._file_dir + self._obj
        elif layer == 2:
            return self._file_dir + self._trk
        elif layer == 3:
            return ((1184, 125, 32, 183), (1472, 124, 32, 183), (1556, 459, 216, 54), (1556, 702, 216, 54),
                    (1408, 773, 32, 183), (1044, 702, 216, 54), (928, 449, 32, 183), (660, 675, 216, 54),
                    (576, 773, 32, 183), (148, 702, 216, 54), (148, 351, 216, 54), (448, 125, 32, 183),
                    (736, 125, 32, 183))
        else:
            raise ValueError("Hairpin.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    @staticmethod
    def start_pos(pos: int):
        """
        Returns the start position and rotation for each position on Hairpin (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return 1107, 177, 270
        elif pos == 2:
            return 1107, 247, 270
        elif pos == 3:
            return 992, 177, 270
        elif pos == 4:
            return 992, 247, 270
        elif pos == 5:
            return 877, 177, 270
        elif pos == 6:
            return 877, 247, 270
        else:
            raise ValueError("Hairpin.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


map_index = [Racetrack(), Snake(), DogBone(), Hairpin()]
