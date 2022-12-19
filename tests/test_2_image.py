import unittest
import main as game


class TestLibrary(unittest.TestCase):
    def test_image_loader(self):
        err_msg = 'Image loader test failed!'

        self.assertRaises(ValueError, game.assets.animation, 'x', 0)
        self.assertRaises(ValueError, game.assets.animation, 'flame', 0, car_num=-1)
        self.assertRaises(ValueError, game.assets.animation, 'flame', 0, car_num='x')
        self.assertEqual(game.assets.animation('lightning', 0),
                         game.assets.assets + '/animations/lightning/frame_0.png', err_msg)
        self.assertEqual(game.assets.animation('flame', 0, car_num='FaMiLy CaR'),
                         game.assets.assets + '/animations/flame/c134f0.png', err_msg)
        self.assertEqual(game.assets.animation('flame', 0, car_num='SpOrTs CaR'),
                         game.assets.assets + '/animations/flame/c2f0.png', err_msg)
        self.assertEqual(game.assets.animation('flame', 0, car_num='RaCe CaR'),
                         game.assets.assets + '/animations/flame/c5f0.png', err_msg)
        self.assertEqual(game.assets.animation('smoke', 0),
                         game.assets.assets + '/animations/smoke/frame_0.png', err_msg)
        self.assertEqual(game.assets.animation('repair', 0),
                         game.assets.assets + '/animations/repair/frame_0.png', err_msg)

        self.assertEqual(game.assets.controller(), game.assets.assets + '/objects/controller.png', err_msg)
        self.assertEqual(game.assets.controller_button('B'),
                         game.assets.assets + '/objects/controller_button_b.png', err_msg)

        self.assertEqual(game.assets.car(game.RED_CAR, 'family car'),
                         game.assets.assets + '/cars/car_red_1.png', err_msg)
        self.assertEqual(game.assets.car(game.YELLOW_CAR, 'sports car'),
                         game.assets.assets + '/cars/car_yellow_2.png', err_msg)
        self.assertEqual(game.assets.car(game.GREEN_CAR, 'luxury car'),
                         game.assets.assets + '/cars/car_green_3.png', err_msg)
        self.assertEqual(game.assets.car(game.BLUE_CAR, 'truck'),
                         game.assets.assets + '/cars/car_blue_4.png', err_msg)
        self.assertEqual(game.assets.car(game.BLACK_CAR, 'race car'),
                         game.assets.assets + '/cars/car_black_5.png', err_msg)
        self.assertRaises(ValueError, game.assets.car, (256, 256, 256), 'family car')
        self.assertRaises(ValueError, game.assets.car, game.RED_CAR, 'x')

        self.assertEqual(game.assets.car_damage('family car', 1),
                         game.assets.assets + '/cars/family_car_damage_1.png', err_msg)

        self.assertEqual(game.assets.traffic_light(0), game.assets.assets + '/objects/traffic_light_0.png', err_msg)

        self.assertEqual(game.assets.power_up('boost'), game.assets.assets + '/powerups/boost_1.png', err_msg)
        self.assertEqual(game.assets.power_up('boost', active=False),
                         game.assets.assets + '/powerups/boost_0.png', err_msg)

        self.assertEqual(game.assets.tile('dirt', 1), game.assets.assets + '/tiles/dirt/land_dirt01.png', err_msg)
        self.assertEqual(game.assets.tile('dirt', 11), game.assets.assets + '/tiles/dirt/land_dirt11.png', err_msg)
        self.assertEqual(game.assets.tile('dirt road', 1),
                         game.assets.assets + '/tiles/dirt_road/road_dirt01.png', err_msg)
        self.assertEqual(game.assets.tile('dirt road', 11),
                         game.assets.assets + '/tiles/dirt_road/road_dirt11.png', err_msg)
        self.assertEqual(game.assets.tile('road', 1), game.assets.assets + '/tiles/road/road_asphalt01.png', err_msg)
        self.assertEqual(game.assets.tile('road', 11), game.assets.assets + '/tiles/road/road_asphalt11.png', err_msg)
        self.assertEqual(game.assets.tile('sand', 1), game.assets.assets + '/tiles/sand/land_sand01.png', err_msg)
        self.assertEqual(game.assets.tile('sand', 11), game.assets.assets + '/tiles/sand/land_sand11.png', err_msg)
        self.assertEqual(game.assets.tile('sand road', 11),
                         game.assets.assets + '/tiles/sand_road/road_sand11.png', err_msg)
