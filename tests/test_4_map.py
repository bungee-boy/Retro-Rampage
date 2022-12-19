import unittest
import main as game


class TestLibrary(unittest.TestCase):
    def test_map_loader(self):
        err_msg = 'Map loader test failed!'
        self.assertEqual(game.maps.map_index, ['racetrack', 'snake', 'dog bone', 'hairpin'], err_msg)

        self.assertRaises(ValueError, game.maps.racetrack, 'x')
        self.assertEqual(game.maps.racetrack('bg'), 'assets/maps/racetrack/bg.png', err_msg)
        self.assertEqual(game.maps.racetrack('obj'), 'assets/maps/racetrack/obj.png', err_msg)
        self.assertEqual(game.maps.racetrack('trk'), 'assets/maps/racetrack/trk.png', err_msg)
        self.assertEqual(game.maps.racetrack('checkpoints'), [[1312, 233, 32, 183], [1428, 513, 215, 53],
                                                              [1376, 665, 32, 183], [928, 665, 32, 183],
                                                              [512, 665, 32, 183], [276, 513, 215, 53],
                                                              [512, 233, 32, 183], [928, 233, 32, 183]], err_msg)

        self.assertRaises(ValueError, game.maps.snake, 'x')
        self.assertEqual(game.maps.snake('bg'), 'assets/maps/snake/bg.png', err_msg)
        self.assertEqual(game.maps.snake('obj'), 'assets/maps/snake/obj.png', err_msg)
        self.assertEqual(game.maps.snake('trk'), 'assets/maps/snake/trk.png', err_msg)
        self.assertEqual(game.maps.snake('checkpoints'), [[930, 773, 32, 183], [1172, 675, 216, 54],
                                                          [1472, 449, 32, 183], [1556, 351, 216, 54],
                                                          [1376, 125, 32, 183], [928, 125, 32, 183],
                                                          [660, 351, 216, 54], [480, 449, 32, 183],
                                                          [148, 675, 216, 54], [544, 773, 32, 183]], err_msg)

        self.assertRaises(ValueError, game.maps.dog_bone, 'x')
        self.assertEqual(game.maps.dog_bone('bg'), 'assets/maps/dog_bone/bg.png', err_msg)
        self.assertEqual(game.maps.dog_bone('obj'), 'assets/maps/dog_bone/obj.png', err_msg)
        self.assertEqual(game.maps.dog_bone('trk'), 'assets/maps/dog_bone/trk.png', err_msg)
        self.assertEqual(game.maps.dog_bone('checkpoints'), [[576, 341, 32, 183], [148, 567, 216, 54],
                                                             [448, 773, 31, 183], [768, 665, 32, 183],
                                                             [1120, 665, 32, 183], [1440, 773, 32, 183],
                                                             [1556, 675, 216, 54], [1556, 432, 216, 54],
                                                             [1521, 125, 31, 183], [1184, 341, 31, 183]], err_msg)

        self.assertRaises(ValueError, game.maps.hairpin, 'x')
        self.assertEqual(game.maps.hairpin('bg'), 'assets/maps/hairpin/bg.png', err_msg)
        self.assertEqual(game.maps.hairpin('obj'), 'assets/maps/hairpin/obj.png', err_msg)
        self.assertEqual(game.maps.hairpin('trk'), 'assets/maps/hairpin/trk.png', err_msg)
        self.assertEqual(game.maps.hairpin('checkpoints'), [[1184, 125, 32, 183], [1472, 124, 32, 183],
                                                            [1556, 459, 216, 54], [1556, 702, 216, 54],
                                                            [1408, 773, 32, 183], [1044, 702, 216, 54],
                                                            [928, 449, 32, 183], [660, 675, 216, 54],
                                                            [576, 773, 32, 183], [148, 702, 216, 54],
                                                            [148, 351, 216, 54], [448, 125, 32, 183],
                                                            [736, 125, 32, 183]], err_msg)
