# Handles map requests and returns appropriate directory path to parent file
# NOTE: Only returns directory path as STRING and does NOT return MAP data!

# Vertical checkpoint: [x, y, 32, 183]
# Horizontal checkpoint: [x, y, 215, 53]

bg_layer = 'bg.png'
obj_layer = 'obj.png'
track_layer = 'trk.png'
maps_dir = 'assets/maps/'
racetrack_dir = maps_dir + 'racetrack/'
snake_dir = maps_dir + 'snake/'
dog_bone_dir = maps_dir + 'dog_bone/'
hairpin_dir = maps_dir + 'hairpin/'
map_index = ['racetrack', 'snake', 'dog bone', 'hairpin']


def racetrack(layer: str):
    if layer == 'bg':
        return racetrack_dir + bg_layer
    elif layer == 'obj':
        return racetrack_dir + obj_layer
    elif layer == 'trk':
        return racetrack_dir + track_layer
    elif layer == 'checkpoints':
        return [[1312, 233, 32, 183], [1428, 513, 215, 53], [1376, 665, 32, 183], [512, 665, 32, 183],
                [928, 665, 32, 183], [276, 513, 215, 53], [512, 233, 32, 183], [928, 233, 32, 183]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj', 'trk' or 'checkpoints' not " + str(layer))


def snake(layer: str):
    if layer == 'bg':
        return snake_dir + bg_layer
    elif layer == 'obj':
        return snake_dir + obj_layer
    elif layer == 'trk':
        return snake_dir + track_layer
    elif layer == 'checkpoints':
        return [[930, 773, 32, 183], [1172, 675, 216, 54], [1472, 449, 32, 183], [1556, 351, 216, 54],
                [1376, 125, 32, 183], [660, 351, 216, 54], [928, 125, 32, 183],
                [480, 449, 32, 183], [148, 675, 216, 54], [544, 773, 32, 183]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj', 'trk' or 'checkpoints' not " + str(layer))


def dog_bone(layer: str):
    if layer == 'bg':
        return dog_bone_dir + bg_layer
    elif layer == 'obj':
        return dog_bone_dir + obj_layer
    elif layer == 'trk':
        return dog_bone_dir + track_layer
    elif layer == 'checkpoints':
        return [[576, 341, 32, 183], [148, 567, 216, 54], [448, 773, 31, 183], [768, 665, 32, 183],
                [1120, 665, 32, 183], [1440, 773, 32, 183], [1556, 675, 216, 54], [1556, 432, 216, 54],
                [1521, 125, 31, 183], [1184, 341, 31, 183]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj', 'trk' or 'checkpoints' not " + str(layer))


def hairpin(layer: str):
    if layer == 'bg':
        return hairpin_dir + bg_layer
    elif layer == 'obj':
        return hairpin_dir + obj_layer
    elif layer == 'trk':
        return hairpin_dir + track_layer
    elif layer == 'checkpoints':
        return [[1184, 125, 32, 183], [1472, 124, 32, 183], [1556, 459, 216, 54], [1556, 702, 216, 54],
                [1408, 773, 32, 183], [1044, 702, 216, 54], [928, 449, 32, 183], [660, 675, 216, 54],
                [576, 773, 32, 183], [148, 702, 216, 54], [148, 351, 216, 54], [448, 125, 32, 183], [736, 125, 32, 183]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj', 'trk' or 'checkpoints' not " + str(layer))
