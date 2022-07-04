# Handles map requests and returns appropriate directory path to parent file
# NOTE: Only returns directory path as STRING and does NOT return MAP data!

bg_layer = 'bg.png'
obj_layer = 'obj.png'
track_layer = 'trk.png'
maps_dir = 'assets\\maps\\'
racetrack_dir = maps_dir + 'racetrack\\'
snake_dir = maps_dir + 'snake\\'
dog_bone_dir = maps_dir + 'dog_bone\\'
hairpin_dir = maps_dir + 'hairpin\\'
map_index = ['racetrack', 'snake', 'dog bone', 'hairpin']


def racetrack(layer):
    if layer == 'bg':
        return racetrack_dir + bg_layer
    elif layer == 'obj':
        return racetrack_dir + obj_layer
    elif layer == 'trk':
        return racetrack_dir + track_layer
    elif layer == 'checkpoints':
        return [[1312, 233, 32, 183], [1376, 665, 32, 183], [512, 665, 32, 183], [512, 233, 32, 183]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj' or 'trk' not " + str(layer))


def snake(layer):
    if layer == 'bg':
        return snake_dir + bg_layer
    elif layer == 'obj':
        return snake_dir + obj_layer
    elif layer == 'trk':
        return snake_dir + track_layer
    elif layer == 'checkpoints':
        return [[930, 773, 32, 183], [1556, 351, 216, 54], [928, 125, 32, 183], [148, 675, 216, 54]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj' or 'trk' not " + str(layer))


def dog_bone(layer):
    if layer == 'bg':
        return dog_bone_dir + bg_layer
    elif layer == 'obj':
        return dog_bone_dir + obj_layer
    elif layer == 'trk':
        return dog_bone_dir + track_layer
    elif layer == 'checkpoints':
        return [[576, 341, 32, 183], [448, 773, 31, 183], [1440, 773, 32, 183], [1521, 125, 31, 183]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj' or 'trk' not " + str(layer))


def hairpin(layer):
    if layer == 'bg':
        return hairpin_dir + bg_layer
    elif layer == 'obj':
        return hairpin_dir + obj_layer
    elif layer == 'trk':
        return hairpin_dir + track_layer
    elif layer == 'checkpoints':
        return [[1184, 125, 32, 183], [1556, 702, 216, 54], [576, 773, 32, 183], [148, 351, 216, 54]]
    else:
        raise ValueError("racetrack(layer) | layer must be 'bg', 'obj' or 'trk' not " + str(layer))
