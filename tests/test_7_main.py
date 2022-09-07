import unittest
import main as game


class TestMain(unittest.TestCase):
    def test_1_variables(self):
        err_msg = 'Variable test failed!'
        self.assertEqual(game.RED, (255, 0, 0), err_msg)
        self.assertEqual(game.WHITE, (255, 255, 255), err_msg)
        self.assertEqual(game.V_LIGHT_GREY, (200, 200, 200), err_msg)
        self.assertEqual(game.LIGHT_GREY, (170, 170, 170), err_msg)
        self.assertEqual(game.GREY, (100, 100, 100), err_msg)
        self.assertEqual(game.BLACK, (0, 0, 0), err_msg)
        self.assertEqual(game.RED_CAR, (232, 106, 23), err_msg)
        self.assertEqual(game.YELLOW_CAR, (255, 204, 0), err_msg)
        self.assertEqual(game.GREEN_CAR, (57, 194, 114), err_msg)
        self.assertEqual(game.BLUE_CAR, (47, 149, 208), err_msg)
        self.assertEqual(game.BLACK_CAR, (93, 91, 91), err_msg)
        self.assertFalse(game.Debug, err_msg)
        self.assertEqual(type(game.Force_resolution), int or list, err_msg)
        self.assertEqual(type(game.Screen), int, err_msg)
        self.assertEqual(type(game.Menu_animation), bool, err_msg)
        self.assertEqual(type(game.Mute_volume), bool, err_msg)
        self.assertEqual(type(game.Music_volume), float, err_msg)
        self.assertEqual(type(game.Sfx_volume), float, err_msg)
        self.assertEqual(game.FPS, 60, err_msg)
        self.assertTrue(game.Intro_screen, err_msg)
        self.assertTrue(game.Countdown, err_msg)
        self.assertTrue(game.Load_settings, err_msg)
        self.assertFalse(game.Game_end, err_msg)
        self.assertEqual(game.WIDTH, 1920, err_msg)
        self.assertEqual(game.HEIGHT, 1080, err_msg)
        self.assertEqual(game.CENTRE, (960, 540), err_msg)
        self.assertEqual(type(game.Window), game.pygame.Surface, err_msg)
        self.assertEqual(game.Window_resolution, (1920, 1080), err_msg)
        self.assertFalse(game.Window_sleep, err_msg)
        self.assertEqual(type(game.Secondary_window), game.pygame.Surface, err_msg)
        self.assertEqual(game.current_window, '', err_msg)
        self.assertEqual(type(game.Display_scaling), bool, err_msg)
        self.assertEqual(game.Players, [], err_msg)
        self.assertEqual(game.Selected_player, [], err_msg)
        self.assertEqual(game.Player_amount, 0, err_msg)
        self.assertEqual(game.Npc_amount, 3, err_msg)
        self.assertEqual(game.Map, 'snake', err_msg)
        self.assertEqual(game.Current_lap, 0, err_msg)
        self.assertEqual(game.Race_time, 0, err_msg)
        self.assertTrue(game.Music_loop, err_msg)
        self.assertEqual(game.Player_positions, [], err_msg)
        self.assertListEqual(game.Npc_names, [['John', False], ['Mark', False], ['Lilly', False], ['Jessica', False],
                                              ['Matthew', False], ['James', False], ['Jack', False], ['Holly', False],
                                              ['Aimee', False], ['Harrison', False], ['Emily', False], ['Ben', False],
                                              ['Tom', False], ['Anthony', False], ['Michael', False], ['Noah', False],
                                              ['Oliver', False], ['Jake', False], ['Olivia', False], ['Teddy', False],
                                              ['Tyler', False], ['Carmel', False], ['Jeremy', False], ['Joe', False],
                                              ['Steven', False], ['Scott', False], ['Keith', False]], err_msg)
        self.assertEqual(game.controllers, [], err_msg)
        self.assertEqual(game.controls, ['wasd', 'arrows'], err_msg)
        self.assertEqual(game.controller_prompts, [], err_msg)
        self.assertEqual(len(game.lightning_frames), 15, err_msg)
        self.assertEqual(game.Npc_force_veh, 0, err_msg)
        self.assertIsNone(game.Npc_force_colour, err_msg)
        self.assertEqual(game.map_preview_size, (974, 600), err_msg)
        self.assertEqual(game.map_preview_pos, (game.CENTRE[0] - game.map_preview_size[0] // 2,
                                                game.CENTRE[1] - game.map_preview_size[1] // 2), err_msg)
        self.assertEqual(game.map_preview, ('', game.map_preview[1]), err_msg)
        self.assertEqual(game.tile_scale, (128, 108), err_msg)
        self.assertEqual(game.menu_scroll_speed, 20, err_msg)
        self.assertEqual(game.menu_car_speed, 6, err_msg)
        self.assertFalse(game.button_trigger, err_msg)
        self.assertEqual(game.selected_text_entry, 0, err_msg)
        self.assertIsNotNone(game.current_song, err_msg)
        self.assertEqual(type(game.clock), game.pygame.time.Clock, err_msg)
        self.assertIsNotNone(game.music_thread, err_msg)
        self.assertTrue(game.powerups, err_msg)
        self.assertFalse(game.Game_paused, err_msg)
        self.assertEqual(game.global_car_rotation_speed, 1, err_msg)
        self.assertEqual(game.global_car_move_speed, 4, err_msg)
        self.assertEqual(type(game.checkpoint_triggers), list, err_msg)
        self.assertEqual(type(game.screen_updates), list, err_msg)
        self.assertEqual(type(game.loaded_assets), list, err_msg)
        self.assertEqual(type(game.loaded_sounds), list, err_msg)
        self.assertEqual(type(game.recorded_keys), list, err_msg)

    def test_2_map_preview(self):
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
