import json
# Returns key input list for NPC paths on every map for every speed combination and diversions
# 0 = FORWARDS, 1 = REVERSE, 2 = LEFT, 3 = RIGHT
# returns [inputs]
# start positions: [[1235, 285], [1235, 355], [1120, 285], [1120, 355], [970, 285], [970, 355]]
# Path code: (rotation_speed)(start_position)(speed)(ver) -> eg. 1221


def diversion(ver):
    if ver == 0:
        return [[1], [1], [0], [0]]
    elif ver == 1:
        return [[0], [0], [1], [1]]


class Racetrack:
    def __init__(self):
        if __name__ == '__main__':
            self.file_dir = 'maps/racetrack/pth.json'
        elif __name__ == 'assets.path_loader':
            self.file_dir = 'assets/maps/racetrack/pth.json'
        with open(self.file_dir, 'r') as paths:
            self.paths = json.load(paths)

    def path(self, rotation: int, start: int, speed: int, ver: int):
        code = 0
        if rotation == 2 or rotation == 3:
            code += rotation*1000
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> rotation == ' + str(rotation))
        if 1 <= start <= 6:
            code += start*100
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> start == ' + str(start))
        if rotation == 2 and 1 <= speed <= 3:
            code += speed*10
        elif rotation == 3 and 1 <= speed <= 5:
            code += speed*10
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> speed == ' + str(speed))
        if 1 <= ver <= 3:
            code += ver
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> ver == ' + str(ver))
        return self.paths[str(code)]

    @staticmethod
    def start_pos(number: int):
        if number == 1:
            return 1235, 285, 270
        elif number == 2:
            return 1235, 355, 270
        elif number == 3:
            return 1120, 285, 270
        elif number == 4:
            return 1120, 355, 270
        elif number == 5:
            return 1005, 285, 270
        elif number == 6:
            return 1005, 355, 270


class Snake:
    def __init__(self):
        if __name__ == '__main__':
            self.file_dir = 'maps/snake/pth.json'
        elif __name__ == 'assets.path_loader':
            self.file_dir = 'assets/maps/snake/pth.json'
        with open(self.file_dir, 'r') as paths:
            self.paths = json.load(paths)

    def path(self, rotation: int, start: int, speed: int, ver: int):
        code = 0
        if rotation == 2 or rotation == 3:
            code += rotation*1000
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> rotation == ' + str(rotation))
        if 1 <= start <= 6:
            code += start*100
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> start == ' + str(start))
        if rotation == 2 and 1 <= speed <= 3:
            code += speed*10
        elif rotation == 3 and 1 <= speed <= 5:
            code += speed*10
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> speed == ' + str(speed))
        if 1 <= ver <= 3:
            code += ver
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> ver == ' + str(ver))
        return self.paths[str(code)]

    @staticmethod
    def start_pos(number: int):
        if number == 1:
            return 853, 825, 270
        elif number == 2:
            return 853, 895, 270
        elif number == 3:
            return 738, 825, 270
        elif number == 4:
            return 738, 895, 270
        elif number == 5:
            return 623, 825, 270
        elif number == 6:
            return 623, 895, 270


class DogBone:
    def __init__(self):
        if __name__ == '__main__':
            self.file_dir = 'maps/dog_bone/pth.json'
        elif __name__ == 'assets.path_loader':
            self.file_dir = 'assets/maps/dog_bone/pth.json'
        with open(self.file_dir, 'r') as paths:
            self.paths = json.load(paths)

    def path(self, rotation: int, start: int, speed: int, ver: int):
        code = 0
        if rotation == 2 or rotation == 3:
            code += rotation*1000
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> rotation == ' + str(rotation))
        if 1 <= start <= 6:
            code += start*100
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> start == ' + str(start))
        if rotation == 2 and 1 <= speed <= 3:
            code += speed*10
        elif rotation == 3 and 1 <= speed <= 5:
            code += speed*10
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> speed == ' + str(speed))
        if 1 <= ver <= 3:
            code += ver
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> ver == ' + str(ver))
        return self.paths[str(code)]

    @staticmethod
    def start_pos(number: int):
        if number == 1:  # 544, 341
            return 685, 393, 90
        elif number == 2:
            return 685, 463, 90
        elif number == 3:
            return 800, 393, 90
        elif number == 4:
            return 800, 463, 90
        elif number == 5:
            return 915, 393, 90
        elif number == 6:
            return 915, 463, 90


class Hairpin:
    def __init__(self):
        if __name__ == '__main__':
            self.file_dir = 'maps/hairpin/pth.json'
        elif __name__ == 'assets.path_loader':
            self.file_dir = 'assets/maps/hairpin/pth.json'
        with open(self.file_dir, 'r') as paths:
            self.paths = json.load(paths)

    def path(self, rotation: int, start: int, speed: int, ver: int):
        code = 0
        if rotation == 2 or rotation == 3:
            code += rotation*1000
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> rotation == ' + str(rotation))
        if 1 <= start <= 6:
            code += start*100
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> start == ' + str(start))
        if rotation == 2 and 1 <= speed <= 3:
            code += speed*10
        elif rotation == 3 and 1 <= speed <= 5:
            code += speed*10
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> speed == ' + str(speed))
        if 1 <= ver <= 3:
            code += ver
        else:
            raise ValueError('path_loader.py | path(rotation, start, speed, ver) -> ver == ' + str(ver))
        return self.paths[str(code)]

    @staticmethod
    def start_pos(number: int):
        if number == 1:
            return 1107, 177, 270
        elif number == 2:
            return 1107, 247, 270
        elif number == 3:
            return 992, 177, 270
        elif number == 4:
            return 992, 247, 270
        elif number == 5:
            return 877, 177, 270
        elif number == 6:
            return 877, 247, 270
