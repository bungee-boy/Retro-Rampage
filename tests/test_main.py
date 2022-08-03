import unittest
import main as game


class TestMain(unittest.TestCase):
    def test_map_preview(self):
        err_msg = 'Map preview test failed!'
        game.Map = 'racetrack'
        game.get_map_preview()
        self.assertEqual(game.map_preview[0], 'racetrack', err_msg)
        game.Map = 'snake'
        game.get_map_preview()
        self.assertEqual(game.map_preview[0], 'snake', err_msg)
        game.Map = 'dog bone'
        game.get_map_preview()
        self.assertEqual(game.map_preview[0], 'dog bone', err_msg)
        game.Map = 'hairpin'
        game.get_map_preview()
        self.assertEqual(game.map_preview[0], 'hairpin', err_msg)
