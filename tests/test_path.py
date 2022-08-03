import unittest
import main as game


class TestLibrary(unittest.TestCase):
    def test_path_loader(self):
        err_msg = 'Path loader test failed!'
        self.assertEqual(game.paths.diversion(0), [[1], [1], [0], [0]], err_msg)
        self.assertEqual(game.paths.diversion(1), [[0], [0], [1], [1]], err_msg)

        racetrack = game.paths.Racetrack()
        self.assertEqual(type(racetrack.paths), dict, err_msg)
        self.assertEqual(type(racetrack.path(2, 1, 2, 1)), list, err_msg)
        self.assertRaises(ValueError, racetrack.path, 1, 0, 0, 0)
        self.assertRaises(ValueError, racetrack.path, 2, 0, 0, 0)
        self.assertRaises(ValueError, racetrack.path, 2, 1, 0, 0)
        self.assertRaises(ValueError, racetrack.path, 2, 1, 2, 0)
        self.assertEqual(racetrack.start_pos(1), (1235, 285, 270), err_msg)
        self.assertEqual(racetrack.start_pos(2), (1235, 355, 270), err_msg)
        self.assertEqual(racetrack.start_pos(3), (1120, 285, 270), err_msg)
        self.assertEqual(racetrack.start_pos(4), (1120, 355, 270), err_msg)
        self.assertEqual(racetrack.start_pos(5), (1005, 285, 270), err_msg)
        self.assertEqual(racetrack.start_pos(6), (1005, 355, 270), err_msg)

        snake = game.paths.Snake()
        self.assertEqual(type(snake.paths), dict, err_msg)
        self.assertEqual(type(snake.path(2, 1, 2, 1)), list, err_msg)
        self.assertRaises(ValueError, snake.path, 1, 0, 0, 0)
        self.assertRaises(ValueError, snake.path, 2, 0, 0, 0)
        self.assertRaises(ValueError, snake.path, 2, 1, 0, 0)
        self.assertRaises(ValueError, snake.path, 2, 1, 2, 0)
        self.assertEqual(snake.start_pos(1), (853, 825, 270), err_msg)
        self.assertEqual(snake.start_pos(2), (853, 895, 270), err_msg)
        self.assertEqual(snake.start_pos(3), (738, 825, 270), err_msg)
        self.assertEqual(snake.start_pos(4), (738, 895, 270), err_msg)
        self.assertEqual(snake.start_pos(5), (623, 825, 270), err_msg)
        self.assertEqual(snake.start_pos(6), (623, 895, 270), err_msg)

        dog_bone = game.paths.DogBone()
        self.assertEqual(type(dog_bone.paths), dict, err_msg)
        self.assertEqual(type(dog_bone.path(2, 1, 2, 1)), list, err_msg)
        self.assertRaises(ValueError, dog_bone.path, 1, 0, 0, 0)
        self.assertRaises(ValueError, dog_bone.path, 2, 0, 0, 0)
        self.assertRaises(ValueError, dog_bone.path, 2, 1, 0, 0)
        self.assertRaises(ValueError, dog_bone.path, 2, 1, 2, 0)
        self.assertEqual(dog_bone.start_pos(1), (685, 393, 90), err_msg)
        self.assertEqual(dog_bone.start_pos(2), (685, 463, 90), err_msg)
        self.assertEqual(dog_bone.start_pos(3), (800, 393, 90), err_msg)
        self.assertEqual(dog_bone.start_pos(4), (800, 463, 90), err_msg)
        self.assertEqual(dog_bone.start_pos(5), (915, 393, 90), err_msg)
        self.assertEqual(dog_bone.start_pos(6), (915, 463, 90), err_msg)

        '''
        hairpin = game.paths.Hairpin()
        self.assertEqual(type(hairpin.paths), dict, err_msg)
        self.assertEqual(type(hairpin.path(2, 1, 2, 1)), list, err_msg)
        self.assertRaises(ValueError, hairpin.path, 1, 0, 0, 0)
        self.assertRaises(ValueError, hairpin.path, 2, 0, 0, 0)
        self.assertRaises(ValueError, hairpin.path, 2, 1, 0, 0)
        self.assertRaises(ValueError, hairpin.path, 2, 1, 2, 0)
        self.assertEqual(hairpin.start_pos(1), (1107, 177, 270), err_msg)
        self.assertEqual(hairpin.start_pos(2), (1107, 247, 270), err_msg)
        self.assertEqual(hairpin.start_pos(3), (992, 177, 270), err_msg)
        self.assertEqual(hairpin.start_pos(4), (992, 247, 270), err_msg)
        self.assertEqual(hairpin.start_pos(5), (877, 177, 270), err_msg)
        self.assertEqual(hairpin.start_pos(6), (877, 247, 270), err_msg)
        '''
