# Handles map requests and returns appropriate directory path to parent file

# Vertical checkpoint: [x, y, 32, 183]
# Horizontal checkpoint: [x, y, 215, 27]


class Racetrack:
    def __init__(self):
        self.name = 'racetrack'
        self._file_dir = 'assets/maps/racetrack/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'
        self._start = 1312, 233

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
            return ((1312, 233, 32, 183), (1428, 513, 215, 27), (1376, 665, 32, 183), (928, 665, 32, 183),
                    (512, 665, 32, 183), (276, 513, 215, 27), (512, 233, 32, 183), (928, 233, 32, 183))
        else:
            raise ValueError("Racetrack.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(self, pos: int):
        """
        Returns the start position and rotation for each position on Racetrack (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return self._start[0] - 77, self._start[1] + 52, 270
        elif pos == 2:
            return self._start[0] - 77, self._start[1] + 122, 270
        elif pos == 3:
            return self._start[0] - 192, self._start[1] + 52, 270
        elif pos == 4:
            return self._start[0] - 192, self._start[1] + 122, 270
        elif pos == 5:
            return self._start[0] - 307, self._start[1] + 52, 270
        elif pos == 6:
            return self._start[0] - 307, self._start[1] + 122, 270
        else:
            raise ValueError("Racetrack.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class Snake:
    def __init__(self):
        self.name = 'snake'
        self._file_dir = 'assets/maps/snake/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'
        self._start = 930, 773

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
            return ((930, 773, 32, 183), (1172, 675, 216, 27), (1472, 449, 32, 183), (1556, 351, 216, 27),
                    (1376, 125, 32, 183), (928, 125, 32, 183), (660, 351, 216, 27), (480, 449, 32, 183),
                    (148, 675, 216, 27), (544, 773, 32, 183))
        else:
            raise ValueError("Snake.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(self, pos: int):
        """
        Returns the start position and rotation for each position on Snake (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return self._start[0] - 77, self._start[1] + 52, 270
        elif pos == 2:
            return self._start[0] - 77, self._start[1] + 122, 270
        elif pos == 3:
            return self._start[0] - 192, self._start[1] + 52, 270
        elif pos == 4:
            return self._start[0] - 192, self._start[1] + 122, 270
        elif pos == 5:
            return self._start[0] - 307, self._start[1] + 52, 270
        elif pos == 6:
            return self._start[0] - 307, self._start[1] + 122, 270
        else:
            raise ValueError("Snake.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class DogBone:
    def __init__(self):
        self.name = 'dog bone'
        self._file_dir = 'assets/maps/dog_bone/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'
        self._start = 706, 341

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
            return ((706, 341, 32, 183), (367, 125, 32, 183), (148, 432, 216, 27), (148, 675, 216, 27),
                    (448, 773, 31, 183), (768, 665, 32, 183), (1120, 665, 32, 183), (1440, 773, 32, 183),
                    (1556, 675, 216, 27), (1556, 432, 216, 27), (1521, 125, 31, 183), (1184, 341, 31, 183))
        else:
            raise ValueError("DogBone.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(self, pos: int):
        """
        Returns the start position and rotation for each position on DogBone (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return self._start[0] + 109, self._start[1] + 52, 90
        elif pos == 2:
            return self._start[0] + 109, self._start[1] + 122, 90
        elif pos == 3:
            return self._start[0] + 224, self._start[1] + 52, 90
        elif pos == 4:
            return self._start[0] + 224, self._start[1] + 122, 90
        elif pos == 5:
            return self._start[0] + 339, self._start[1] + 52, 90
        elif pos == 6:
            return self._start[0] + 339, self._start[1] + 122, 90
        else:
            raise ValueError("DogBone.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class Hairpin:
    def __init__(self):
        self.name = 'hairpin'
        self._file_dir = 'assets/maps/hairpin/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'
        self._start = 1184, 125

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
            return ((1184, 125, 32, 183), (1472, 124, 32, 183), (1556, 459, 216, 27), (1556, 702, 216, 27),
                    (1408, 773, 32, 183), (1044, 702, 216, 27), (928, 449, 32, 183), (660, 675, 216, 27),
                    (576, 773, 32, 183), (148, 702, 216, 27), (148, 351, 216, 27), (448, 125, 32, 183),
                    (736, 125, 32, 183))
        else:
            raise ValueError("Hairpin.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(self, pos: int):
        """
        Returns the start position and rotation for each position on Hairpin (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return self._start[0] - 77, self._start[1] + 52, 270
        elif pos == 2:
            return self._start[0] - 77, self._start[1] + 122, 270
        elif pos == 3:
            return self._start[0] - 192, self._start[1] + 52, 270
        elif pos == 4:
            return self._start[0] - 192, self._start[1] + 122, 270
        elif pos == 5:
            return self._start[0] - 307, self._start[1] + 52, 270
        elif pos == 6:
            return self._start[0] - 307, self._start[1] + 122, 270
        else:
            raise ValueError("Hairpin.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class Pinch:
    def __init__(self):
        self.name = 'pinch'
        self._file_dir = 'assets/maps/pinch/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'
        self._start = 704, 773

    def layer(self, layer: int):
        """
        Returns a layer of the Pinch track
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
            return ((704, 773, 32, 183), (148, 675, 215, 27), (448, 449, 32, 183), (660, 324, 215, 27),
                    (992, 125, 32, 183), (1280, 341, 32, 183), (1556, 540, 215, 27), (1504, 773, 32, 183),
                    (1120, 773, 32, 183))
        else:
            raise ValueError("Pinch.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(self, pos: int):
        """
        Returns the start position and rotation for each position on Pinch (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return self._start[0] + 109, self._start[1] + 52, 90
        elif pos == 2:
            return self._start[0] + 109, self._start[1] + 122, 90
        elif pos == 3:
            return self._start[0] + 224, self._start[1] + 52, 90
        elif pos == 4:
            return self._start[0] + 224, self._start[1] + 122, 90
        elif pos == 5:
            return self._start[0] + 339, self._start[1] + 52, 90
        elif pos == 6:
            return self._start[0] + 339, self._start[1] + 122, 90
        else:
            raise ValueError("Pinch.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class TBone:
    def __init__(self):
        self.name = 'tbone'
        self._file_dir = 'assets/maps/t_bone/'
        self._bg = 'bg.png'
        self._obj = 'obj.png'
        self._trk = 'trk.png'
        self._start = 1060, 449

    def layer(self, layer: int):
        """
        Returns a layer of the Pinch track
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
            return ((1060, 449, 32, 183), (1172, 351, 215, 27), (1440, 125, 32, 183), (1556, 351, 215, 27),
                    (1556, 675, 215, 27), (1440, 773, 32, 183), (960, 773, 32, 183), (416, 773, 32, 183),
                    (148, 675, 215, 27), (448, 449, 32, 183))
        else:
            raise ValueError("Pinch.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(self, pos: int):
        """
        Returns the start position and rotation for each position on Pinch (1 - 6)
        [0] = Pos X
        [1] = Pos Y
        [2] = Rotation
        """
        if pos == 1:
            return self._start[0] - 77, self._start[1] + 52, 270
        elif pos == 2:
            return self._start[0] - 77, self._start[1] + 122, 270
        elif pos == 3:
            return self._start[0] - 192, self._start[1] + 52, 270
        elif pos == 4:
            return self._start[0] - 192, self._start[1] + 122, 270
        elif pos == 5:
            return self._start[0] - 307, self._start[1] + 52, 270
        elif pos == 6:
            return self._start[0] - 307, self._start[1] + 122, 270
        else:
            raise ValueError("Pinch.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


index = ('racetrack', 'snake', 'dog bone', 'hairpin', 'pinch', 'tbone')
objs = (Racetrack, Snake, DogBone, Hairpin, Pinch, TBone)
