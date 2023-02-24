import unittest
import main as game
from time import sleep


class TestMain(unittest.TestCase):
    @staticmethod
    def show_screen(screen=game.Window):
        game.Display.blit(game.pygame.transform.scale(screen, game.Display_resolution), (0, 0))
        game.pygame.display.update()
        sleep(0.2)
        screen.fill(game.BLACK)
        screen.blit(game.pygame.font.Font(game.fonts.load(bar=True), 100).render(
            'Retro Rampage', True, game.WHITE), (game.CENTRE[0] - 412, game.CENTRE[1] - 60))
        screen.blit(game.pygame.font.Font(game.fonts.load(), 100).render(
            'Testing mode', True, game.WHITE), (game.CENTRE[0] - 346, game.CENTRE[1] + 60))

    @staticmethod
    def keypress(keys):  # Used to simulate keyboard input
        def keyboard():
            board = [0] * 300
            if type(keys) == int:
                board[keys] = 1
            else:
                for key in keys:
                    board[key] = 1
            return board

        return keyboard

    def test_1_variables(self):
        err_msg = 'Variable test failed!'
        self.assertEqual(game.RED, (255, 0, 0), err_msg)
        self.assertEqual(game.WHITE, (255, 255, 255), err_msg)
        self.assertEqual(game.V_LIGHT_GREY, (200, 200, 200), err_msg)
        self.assertEqual(game.LIGHT_GREY, (170, 170, 170), err_msg)
        self.assertEqual(game.GREY, (150, 150, 150), err_msg)
        self.assertEqual(game.BLACK, (0, 0, 0), err_msg)
        self.assertEqual(game.RED_CAR, (232, 106, 23), err_msg)
        self.assertEqual(game.YELLOW_CAR, (255, 204, 0), err_msg)
        self.assertEqual(game.GREEN_CAR, (57, 194, 114), err_msg)
        self.assertEqual(game.BLUE_CAR, (47, 149, 208), err_msg)
        self.assertEqual(game.BLACK_CAR, (93, 91, 91), err_msg)
        self.assertFalse(game.Debug, err_msg)
        self.assertEqual(type(game.Force_resolution), int or list, err_msg)
        self.assertEqual(type(game.Screen), int, err_msg)
        self.assertEqual(type(game.Animations), bool, err_msg)
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
        self.assertEqual(type(game.Players), list, err_msg)
        self.assertEqual(game.Selected_player, [], err_msg)
        self.assertEqual(game.Player_amount, 2, err_msg)
        self.assertEqual(game.Npc_amount, 1, err_msg)
        self.assertEqual(game.Map.name, game.maps.objs[len(game.maps.index)//2]().name, err_msg)
        self.assertEqual(game.Current_lap, 0, err_msg)
        self.assertEqual(game.Race_time, 0, err_msg)
        self.assertEqual(game.Player_positions, [], err_msg)
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
        self.assertEqual(game.menu_scroll_speed, 70, err_msg)
        self.assertEqual(game.menu_car_speed, 10, err_msg)
        self.assertFalse(game.button_trigger, err_msg)
        self.assertEqual(game.selected_text_entry, 0, err_msg)
        self.assertIsNotNone(game.current_song, err_msg)
        self.assertIsNotNone(game.Clock, err_msg)
        self.assertIsNotNone(game.music_thread, err_msg)
        self.assertTrue(game.powerups, err_msg)
        self.assertFalse(game.Game_paused, err_msg)
        self.assertEqual(game.global_car_rotation_speed, 1, err_msg)
        self.assertEqual(game.global_car_move_speed, 4, err_msg)
        # self.assertEqual(type(game.checkpoint_triggers), list, err_msg)
        self.assertEqual(type(game.screen_updates), list, err_msg)
        self.assertEqual(type(game.loaded_assets), list, err_msg)
        self.assertEqual(type(game.loaded_sounds), list, err_msg)
        self.assertEqual(type(game.loaded_fonts), dict, err_msg)

    def test_2_map_preview(self):
        game.Map = game.maps.objs[0]()
        game.get_map_preview()
        game.Map = game.maps.objs[1]()
        game.get_map_preview()
        game.Map = game.maps.objs[2]()
        game.get_map_preview()
        game.Map = game.maps.objs[3]()
        game.get_map_preview()

    def test_3_object(self):
        surf = game.pygame.surface.Surface
        rect = game.pygame.rect.Rect
        mask = game.pygame.mask.Mask
        obj = game.Object(surf, rect, mask)
        self.assertEqual(obj.surf, surf)
        self.assertEqual(obj.rect, rect)
        self.assertEqual(obj.mask, mask)

    def test_4_windows(self):
        surf = game.pygame.surface.Surface((1920, 1080))
        surf.blit(game.pygame.image.load(game.maps.Racetrack().layer(0)), (0, 0))

        game.main_window(surf)
        self.show_screen()

        game.choose_map_window(surf)
        self.show_screen()

        game.controls = []
        game.Players = [game.Player(0), game.Player(1), game.Player(2), game.Player(3), game.Player(4), game.Player(5)]
        game.controllers = [0, 1, 2, 3]
        for player_amount in range(1, 7):
            game.Player_amount = player_amount
            game.choose_players_window(surf)
            self.show_screen()

        for player_amount in range(3, 7):
            game.Player_amount = player_amount
            game.choose_players_window_2(surf)
            self.show_screen()

        for player_amount in range(5, 7):
            game.Player_amount = player_amount
            game.choose_players_window_3(surf)
            self.show_screen()

        for player_amount in range(1, 3):
            game.Player_amount = player_amount
            game.choose_vehicle_window(surf)
            self.show_screen()

        for player_amount in range(3, 5):
            game.Player_amount = player_amount
            game.choose_vehicle_window_2(surf)
            self.show_screen()

        for player_amount in range(5, 7):
            game.Player_amount = player_amount
            game.choose_vehicle_window_3(surf)
            self.show_screen()

        for player_amount in range(1, 7):
            game.Player_amount = player_amount
            game.race_settings_window(surf)
            self.show_screen()

        game.confirm_quit_window(surf)
        self.show_screen()

        game.credits_window(surf)
        self.show_screen()

        game.tutorial_window(surf)
        self.show_screen()

        game.settings_window(surf)
        self.show_screen()

        game.leaderboard_window(surf)
        self.show_screen()

        game.player_list = [game.Car(game.Players[0]), game.Car(game.Players[1]), game.Car(game.Players[1]),
                            game.Car(game.Players[1]), game.Car(game.Players[1]), game.Car(game.Players[1])]
        for player_amount in range(1, 3):
            game.Player_amount = player_amount
            game.gameplay_gui(game.player_list, 0, 0)
            self.show_screen()

        game.paused_window()
        self.show_screen(game.Secondary_window)

        new_surf = game.menu_background(top=True, right=True, bottom=True, left=True)
        game.animate_window(game.main_window, game.credits_window, surf, new_surf, game.MenuCar, 'u')
        self.show_screen()

    def test_5_functions(self):
        game.controller_prompts = [['Controller 1', True, game.pygame.time.get_ticks() + 4000],
                                   ['Controller 2', False, game.pygame.time.get_ticks() + 4000]]
        game.controller_popup()
        self.show_screen()

        game.Display.blit(game.render_key('A'), (0, 0))
        game.Display.blit(game.render_key('right'), (0, 51))
        self.show_screen()

        game.fade_to_black(show_loading=True)
        game.loading_thread_event.clear()
        game.loading_thread = game.Thread(name='loading_thread', target=game.loading_animation,
                                          args=(game.CENTRE[0], game.CENTRE[1] + 300))
        game.loading_thread.start()  # Begin loading animation
        sleep(1)
        game.loading_thread_event.set()
        game.loading_thread.join()
        game.fade_from_black(show_loading=True)

        game.decrease_resolution()
        sleep(0.1)
        game.increase_resolution()

    def test_6_game(self):
        self.show_screen()
        game.fade_to_black()

        game.controls = []
        game.Player_amount = 1
        game.Players = [game.Player(0)]
        game.Players[0].name = 'TESTING'
        game.Npc_amount = 1
        game.pygame.mouse.set_pos(game.CENTRE[0], game.CENTRE[1])
        game.Map = game.maps.Racetrack()
        game.Debug = False
        game_thread = game.Thread(name='game_thread', target=game.game)
        game_thread.start()
        sleep(12)
        game.Game_end = True
        game_thread.join()
        self.show_screen()

        game.Map = game.maps.Snake()
        game.Debug = True
        game_thread = game.Thread(name='game_thread', target=game.game)
        game_thread.start()
        sleep(5)
        game.Game_end = True
        game_thread.join()
        self.show_screen()

        game.Map = game.maps.DogBone()
        game.Debug = False
        game.Countdown = False
        game.Animations = False
        game_thread = game.Thread(name='game_thread', target=game.game)
        game_thread.start()
        sleep(2)
        game.Game_end = True
        game_thread.join()
        self.show_screen()

        for index in range(3, len(game.maps.objs) - 1):
            game.Debug = False
            game.Countdown = False
            game.Animations = False
            game.Map = game.maps.objs[index]()
            game_thread = game.Thread(name='game_thread', target=game.game)
            game_thread.start()
            sleep(2)
            game.Game_end = True
            game_thread.join()
            self.show_screen()

        game.Map = game.maps.objs[len(game.maps.objs) - 1]()
        game.Countdown = False
        game_thread = game.Thread(name='game_thread', target=game.game)
        game_thread.start()
        sleep(5)
        game.pygame.event.post(game.pygame.event.Event(game.pygame.KEYDOWN, key=game.pygame.K_ESCAPE))
        sleep(1)
        self.assertTrue(game.Game_paused)
        sleep(1)
        game.pygame.event.post(game.pygame.event.Event(game.pygame.KEYDOWN, key=game.pygame.K_ESCAPE))
        sleep(1)
        self.assertFalse(game.Game_paused)
        sleep(1)
        game.Animations = False
        game.Game_end = True
        if game.loading_thread.is_alive():
            game.loading_thread.join()
        game_thread.join()
        self.show_screen()

        game.Countdown = True
