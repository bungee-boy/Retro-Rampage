import unittest
import main as game


class TestLibrary(unittest.TestCase):
    def test_map_loader(self):
        err_msg = 'Map loader test failed!'
        self.assertEqual(game.maps.index, ('racetrack', 'snake', 'dog bone', 'hairpin', 'pinch',
                                           't bone', 'bridge', 'overhang', 'fernando', 'crumple'), err_msg)
        self.assertEqual(game.maps.objs, (game.maps.Racetrack, game.maps.Snake, game.maps.DogBone, game.maps.Hairpin,
                                          game.maps.Pinch, game.maps.TBone, game.maps.Bridge, game.maps.Overhang,
                                          game.maps.Fernando, game.maps.Crumple), err_msg)

        map_obj = game.maps.Racetrack()
        self.assertEqual(map_obj.layer(3), ((1312, 233, 32, 183), (1428, 513, 215, 27), (1376, 665, 32, 183),
                                            (928, 665, 32, 183), (512, 665, 32, 183), (276, 513, 215, 27),
                                            (512, 233, 32, 183), (928, 233, 32, 183)), err_msg)

        map_obj = game.maps.Snake()
        self.assertEqual(map_obj.layer(3), ((930, 773, 32, 183), (1172, 675, 216, 27), (1472, 449, 32, 183),
                                            (1556, 351, 216, 27), (1376, 125, 32, 183), (928, 125, 32, 183),
                                            (660, 351, 216, 27), (480, 449, 32, 183), (148, 675, 216, 27),
                                            (544, 773, 32, 183)), err_msg)

        map_obj = game.maps.DogBone()
        self.assertEqual(map_obj.layer(3), ((706, 341, 32, 183), (367, 125, 32, 183), (148, 432, 216, 27),
                                            (148, 675, 216, 27), (448, 773, 31, 183), (768, 665, 32, 183),
                                            (1120, 665, 32, 183), (1440, 773, 32, 183), (1556, 675, 216, 27),
                                            (1556, 432, 216, 27), (1521, 125, 31, 183), (1184, 341, 31, 183)), err_msg)

        map_obj = game.maps.Hairpin()
        self.assertEqual(map_obj.layer(3),
                         ((1184, 125, 32, 183), (1472, 124, 32, 183), (1556, 459, 216, 27), (1556, 702, 216, 27),
                          (1408, 773, 32, 183), (1044, 702, 216, 27), (928, 449, 32, 183), (660, 675, 216, 27),
                          (576, 773, 32, 183), (148, 702, 216, 27), (148, 351, 216, 27), (448, 125, 32, 183),
                          (736, 125, 32, 183)), err_msg)

        map_obj = game.maps.Pinch()
        self.assertEqual(map_obj.layer(3), ((704, 773, 32, 183), (148, 675, 215, 27), (448, 449, 32, 183),
                                            (660, 324, 215, 27), (992, 125, 32, 183), (1280, 341, 32, 183),
                                            (1556, 540, 215, 27), (1504, 773, 32, 183), (1120, 773, 32, 183)), err_msg)

        map_obj = game.maps.TBone()
        self.assertEqual(map_obj.layer(3), ((1060, 449, 32, 183), (1172, 351, 215, 27), (1440, 125, 32, 183),
                                            (1556, 351, 215, 27), (1556, 675, 215, 27), (1440, 773, 32, 183),
                                            (960, 773, 32, 183), (416, 773, 32, 183), (148, 675, 215, 27),
                                            (448, 449, 32, 183)), err_msg)

        map_obj = game.maps.Bridge()
        self.assertEqual(map_obj.layer(3), ((1444, 125, 32, 183), (1556, 432, 215, 27), (1556, 702, 215, 27),
                                            (1440, 773, 32, 183), (1172, 675, 215, 27), (1056, 449, 32, 183),
                                            (788, 675, 215, 27), (704, 773, 32, 183), (416, 773, 32, 183),
                                            (148, 675, 215, 27), (416, 449, 31, 183), (532, 378, 215, 27),
                                            (768, 125, 32, 183), (992, 125, 32, 183)), err_msg)

        map_obj = game.maps.Overhang()
        self.assertEqual(map_obj.layer(3), ((1060, 125, 32, 183), (1172, 351, 215, 27), (1440, 449, 32, 183),
                                            (1556, 675, 215, 27), (1472, 773, 32, 183), (1184, 773, 32, 183),
                                            (916, 675, 215, 27), (832, 449, 32, 183), (416, 449, 32, 183),
                                            (148, 351, 215, 27), (416, 125, 32, 183), (672, 125, 32, 183)), err_msg)

        map_obj = game.maps.Fernando()
        self.assertEqual(map_obj.layer(3), ((1316, 125, 32, 183), (1556, 324, 215, 27), (1300, 648, 215, 27),
                                            (1215, 773, 32, 183), (916, 675, 215, 27), (800, 449, 32, 183),
                                            (532, 676, 215, 27), (448, 773, 32, 183), (148, 675, 215, 27),
                                            (148, 351, 215, 27), (448, 125, 32, 183), (864, 125, 32, 183)), err_msg)

        map_obj = game.maps.Crumple()
        self.assertEqual(map_obj.layer(3), ((1218, 773, 32, 183), (864, 557, 32, 183), (480, 773, 32, 183),
                                            (148, 702, 215, 27), (148, 540, 215, 27), (416, 341, 32, 183),
                                            (768, 125, 32, 183), (1137, 341, 32, 183), (1408, 125, 32, 183),
                                            (1556, 351, 215, 27), (1556, 648, 215, 27)), err_msg)

        for map_obj in game.maps.objs:
            map_obj = map_obj()
            self.assertIn(map_obj.name, game.maps.index)
            self.assertRaises(ValueError, map_obj.layer, -1)
            self.assertEqual(map_obj.layer(0),
                             'assets/maps/{0}/bg.png'.format(map_obj.name.lower().replace(' ', '_')), err_msg)
            self.assertEqual(map_obj.layer(1),
                             'assets/maps/{0}/obj.png'.format(map_obj.name.lower().replace(' ', '_')), err_msg)
            self.assertEqual(map_obj.layer(2),
                             'assets/maps/{0}/trk.png'.format(map_obj.name.lower().replace(' ', '_')), err_msg)
            self.assertRaises(ValueError, map_obj.layer, 4)
            self.assertRaises(ValueError, map_obj.start_pos, 0)
            self.assertEqual(type(map_obj.start_pos(1)), tuple, err_msg)
            self.assertEqual(type(map_obj.start_pos(2)), tuple, err_msg)
            self.assertEqual(type(map_obj.start_pos(3)), tuple, err_msg)
            self.assertEqual(type(map_obj.start_pos(4)), tuple, err_msg)
            self.assertEqual(type(map_obj.start_pos(5)), tuple, err_msg)
            self.assertEqual(type(map_obj.start_pos(6)), tuple, err_msg)
            self.assertRaises(ValueError, map_obj.start_pos, 7)
