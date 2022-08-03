import unittest
import main as game

car = game.Car(game.Player(0))
car_2 = game.Car(game.Player(1))
npc = game.NPCCar(1, game.RED_CAR, (40, 70), 'npc', 'racetrack', 1)


def keypress(keys):   # Used to simulate keyboard input
    def keyboard():
        board = [0] * 300
        if type(keys) == int:
            board[keys] = 1
        else:
            for key in keys:
                board[key] = 1
        return board
    return keyboard


def reset_car(vehicle):  # Used to reset the car's position when testing movement
    vehicle.move(0, 0)
    vehicle.rotate(180)


reset_car(car)
reset_car(car_2)


class TestPlayer(unittest.TestCase):
    def test_load_defaults(self):
        player = game.Player(0)
        self.assertEqual(player.id, 0)
        self.assertEqual(player.veh_name, 'Family Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.RED_CAR, 'Loading player defaults failed!')
        if 'wasd' not in game.controls:
            self.assertEqual(player.controls, 'wasd', 'Loading player defaults failed!')
        elif 'arrows' not in game.controls:
            self.assertEqual(player.controls, 'arrows', 'Loading player defaults failed!')
        else:
            self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, 6 - player.id, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(1)
        self.assertEqual(player.id, 1)
        self.assertEqual(player.veh_name, 'Sports Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.YELLOW_CAR, 'Loading player defaults failed!')
        if 'wasd' not in game.controls:
            self.assertEqual(player.controls, 'wasd', 'Loading player defaults failed!')
        elif 'arrows' not in game.controls:
            self.assertEqual(player.controls, 'arrows', 'Loading player defaults failed!')
        else:
            self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, 6 - player.id, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(2)
        self.assertEqual(player.id, 2)
        self.assertEqual(player.veh_name, 'Luxury Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.GREEN_CAR, 'Loading player defaults failed!')
        if 'wasd' not in game.controls:
            self.assertEqual(player.controls, 'wasd', 'Loading player defaults failed!')
        elif 'arrows' not in game.controls:
            self.assertEqual(player.controls, 'arrows', 'Loading player defaults failed!')
        else:
            self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, 6 - player.id, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(3)
        self.assertEqual(player.id, 3)
        self.assertEqual(player.veh_name, 'Truck', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.BLUE_CAR, 'Loading player defaults failed!')
        if 'wasd' not in game.controls:
            self.assertEqual(player.controls, 'wasd', 'Loading player defaults failed!')
        elif 'arrows' not in game.controls:
            self.assertEqual(player.controls, 'arrows', 'Loading player defaults failed!')
        else:
            self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, 6 - player.id, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(4)
        self.assertEqual(player.id, 4)
        self.assertEqual(player.veh_name, 'Race Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.BLACK_CAR, 'Loading player defaults failed!')
        if 'wasd' not in game.controls:
            self.assertEqual(player.controls, 'wasd', 'Loading player defaults failed!')
        elif 'arrows' not in game.controls:
            self.assertEqual(player.controls, 'arrows', 'Loading player defaults failed!')
        else:
            self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, 6 - player.id, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(5)
        self.assertEqual(player.id, 5)
        self.assertEqual(player.veh_name, 'Family Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.RED_CAR, 'Loading player defaults failed!')
        if 'wasd' not in game.controls:
            self.assertEqual(player.controls, 'wasd', 'Loading player defaults failed!')
        elif 'arrows' not in game.controls:
            self.assertEqual(player.controls, 'arrows', 'Loading player defaults failed!')
        else:
            self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, 6 - player.id, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')


class TestCar(unittest.TestCase):
    def test_movement(self):
        car.move(0, 0)
        self.assertTupleEqual(car.rect.center, (0, 0), 'Failed to move to 0, 0!')
        car.move(100, 0)
        self.assertTupleEqual(car.rect.center, (100, 0), 'Failed to move to 100, 0!')
        car.move(0, 100)
        self.assertTupleEqual(car.rect.center, (0, 100), 'Failed to move to 0, 100!')

    def test_rotation(self):
        car.rotate(2)
        self.assertEqual(car.rotation, 0, 'Snapping to 0 from 2 failed!')
        car.rotate(358)
        self.assertEqual(car.rotation, 0, 'Snapping to 0 from 358 failed!')
        car.rotate(92)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 92 failed!')
        car.rotate(88)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 88 failed!')

    def test_set_controls(self):
        car.set_controls('wasd')
        self.assertEqual(car.input_type, 'keyboard', 'Keyboard control failed!')
        self.assertEqual(car._up, game.pygame.K_w, 'W key control failed!')
        self.assertEqual(car._down, game.pygame.K_s, 'S key control failed!')
        self.assertEqual(car._left, game.pygame.K_a, 'A key control failed!')
        self.assertEqual(car._right, game.pygame.K_d, 'D key control failed!')

        car.set_controls('arrows')
        self.assertEqual(car._up, game.pygame.K_UP, 'Up arrow key control failed!')
        self.assertEqual(car._down, game.pygame.K_DOWN, 'Down arrow key control failed!')
        self.assertEqual(car._left, game.pygame.K_LEFT, 'Left arrow control key failed!')
        self.assertEqual(car._right, game.pygame.K_RIGHT, 'Right arrow control key failed!')

        import platform
        if platform.system() == 'Windows':
            try:
                self.controller = game.pygame.joystick.Joystick(0)
                game.controllers.append(self.controller)  # Connect dummy controller
                car.set_controls(self.controller)  # Bind car to dummy controller
                self.assertEqual(car.controller, self.controller, 'Binding controller failed!')
                print(self.controller.get_axis())
            except game.pygame.error:
                print('\n** Connect a controller to run controller tests **')
        else:
            print('\n** Run tests on windows to check controller inputs **')

    def test_check_laps(self):
        reset_car(car)
        car.check_laps(game.pygame.rect.Rect(0, 0, car.rect.width, car.rect.height),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide lap
        self.assertTrue(car._lap_collision, 'Lap collision failed!')
        self.assertEqual(car.laps, 1, 'Initial lap failed!')
        car.check_laps(game.pygame.rect.Rect(0, 0, car.rect.width, car.rect.height),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide lap
        self.assertEqual(car.laps, 1, 'Lap incremented twice!')
        car.check_laps(game.pygame.rect.Rect(100, 100, 1, 1),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide none
        self.assertFalse(car._lap_collision, "Lap collision didn't reset!")
        car.check_laps(game.pygame.rect.Rect(200, 200, 1, 1),  # Collide halfway
                       game.pygame.rect.Rect(0, 0, car.rect.width, car.rect.height))
        self.assertTrue(car._lap_collision, 'Lap collision failed!')
        self.assertTrue(car._lap_halfway, 'Lap halfway failed!')
        self.assertEqual(car.laps, 1, 'Lap increased on halfway trigger!')
        car.check_laps(game.pygame.rect.Rect(100, 100, 1, 1),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide none
        self.assertFalse(car._lap_collision, "Lap collision didn't reset on halfway!")
        car.check_laps(game.pygame.rect.Rect(0, 0, car.rect.width, car.rect.height),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide lap
        self.assertFalse(car._lap_halfway, "Lap halfway didn't reset!")
        self.assertEqual(car.laps, 2, 'Lap increase failed!')

    def test_check_checkpoints(self):
        reset_car(car)
        game.checkpoint_triggers = [[], []]
        car._checkpoint_collision = False
        car.check_checkpoints([game.pygame.rect.Rect(0, 0, car.rect.width, car.rect.height)])
        self.assertTrue(car._checkpoint_collision, 'Checkpoint trigger failed!')
        self.assertTrue(car._point_checked, 'Checkpoint trigger failed!')
        self.assertIn([car.name, car.laps, car._image_dir], game.checkpoint_triggers[0], 'Checkpoint trigger failed!')
        car.check_checkpoints([game.pygame.rect.Rect(0, 0, car.rect.width, car.rect.height)])
        self.assertNotIn([car.name, car.laps, car._image_dir], game.checkpoint_triggers[1], 'Checkpoint added twice!')
        car.check_checkpoints([game.pygame.rect.Rect(100, 100, 1, 1)])
        self.assertFalse(car._checkpoint_collision, 'Checkpoint reset failed!')
        self.assertFalse(car._point_checked, 'Checkpoint reset failed!')

    def test_clear_checkpoints(self):
        car.check_checkpoints([game.pygame.rect.Rect(0, 0, car.rect.width, car.rect.height)])
        car.clear_checkpoints()
        self.assertNotIn([car.name, car.laps, car._image_dir], game.checkpoint_triggers[0], 'Clear checkpoints failed!')

    def test_track_collision(self):
        reset_car(car)
        car.collision = False
        car._collision_sound = False
        car.damage = 0
        mask = game.pygame.surface.Surface((100, 100))
        mask_overlay = game.pygame.surface.Surface((50, 100))
        mask.fill((0, 0, 0))
        mask_overlay.fill((255, 255, 255))
        mask.blit(mask_overlay, (0, 0))
        mask.set_colorkey((0, 0, 0))
        mask = game.pygame.mask.from_surface(mask)
        car.check_track_collisions(mask)
        self.assertEqual(car.collision, 'track', 'Track collision failed!')
        self.assertTrue(car._collision_sound, 'Track collision failed!')
        self.assertEqual(car.damage, 1, 'Track collision failed!')
        car.check_track_collisions(mask)
        self.assertEqual(car.damage, 1, 'Track collision triggered twice!')
        car.move(200, 200)
        car.check_track_collisions(mask)
        self.assertFalse(car.collision, 'Track collision failed to reset!')
        self.assertFalse(car._collision_sound, 'Track collision failed to reset!')
        self.assertTrue(car._allow_forwards, 'Track collision failed to reset!')
        self.assertTrue(car._allow_reverse, 'Track collision failed to reset!')
        '''
        car.rotate(0)
        car.rect.midbottom = 20, 20
        self.assertFalse(car._allow_forwards, 'Track top collision failed!')
        self.assertTrue(car._allow_reverse, 'Track top collision failed!')
        car.rect.midtop = 20, 80
        car.check_track_collisions(mask)
        self.assertTrue(car._allow_forwards, 'Track bottom collision failed!')
        self.assertFalse(car._allow_reverse, 'Track bottom collision failed!')
        car.rotate(180)
        car.rect.midbottom = 20, 20
        car.check_track_collisions(mask)
        self.assertTrue(car._allow_forwards, 'Track top collision failed!')
        self.assertFalse(car._allow_reverse, 'Track top collision failed!')
        car.rect.midtop = 20, 80
        car.check_track_collisions(mask)
        self.assertFalse(car._allow_forwards, 'Track bottom collision failed!')
        self.assertTrue(car._allow_reverse, 'Track bottom collision failed!')
        car.rotate(90)
        car.midright = 20, 50
        car.check_track_collisions(mask)
        self.assertTrue(car._allow_forwards, 'Track left collision failed!')
        self.assertFalse(car._allow_reverse, 'Track left collision failed!')
        car.midleft = 30, 50
        car.check_track_collisions(mask)
        self.assertFalse(car._allow_forwards, 'Track right collision failed!')
        self.assertTrue(car._allow_reverse, 'Track right collision failed!')
        car.rotate(270)
        car.midright = 20, 50
        car.check_track_collisions(mask)
        self.assertFalse(car._allow_forwards, 'Track left collision failed!')
        self.assertTrue(car._allow_reverse, 'Track left collision failed!')
        car.midleft = 30, 50
        car.check_track_collisions(mask)
        self.assertTrue(car._allow_forwards, 'Track right collision failed!')
        self.assertFalse(car._allow_reverse, 'Track right collision failed!')
        '''

    def test_car_collision(self):
        reset_car(car)
        reset_car(car_2)
        car.check_car_collision(car_2)
        self.assertEqual(car.collision, car_2, 'Car collision failed!')
        car_2.move(100, 0)
        car.check_car_collision(car_2)
        self.assertFalse(car.collision, 'Car collision did not reset!')
        car_2.move(0, car.rect.height-2)
        car.check_car_collision(car_2)
        self.assertFalse(car._allow_forwards, 'Front collision did not stop!')
        self.assertTrue(car._allow_reverse, 'Front collision did not stop!')
        car_2.move(0, -car.rect.height+2)
        car.check_car_collision(car_2)
        self.assertFalse(car._allow_reverse, 'Rear collision did not stop!')
        self.assertTrue(car._allow_forwards, 'Rear collision did not stop!')

    def test_input(self):
        car._allow_forwards = True
        car._allow_reverse = True
        car.set_controls('wasd')
        reset_car(car)
        game.pygame.key.get_pressed = keypress(game.pygame.K_w)
        car.check_inputs()
        self.assertGreater(car.pos_y, 0, 'W input failed!')

        reset_car(car)
        game.pygame.key.get_pressed = keypress(game.pygame.K_s)
        car.check_inputs()
        self.assertLess(car.pos_y, 0, 'S input failed!')

        reset_car(car)
        game.pygame.key.get_pressed = keypress([game.pygame.K_w, game.pygame.K_a])
        car.check_inputs()
        self.assertGreater(car.pos_y, 0, 'W & A input failed!')
        self.assertGreater(car.rotation, 180, 'W & A input failed!')

        reset_car(car)
        game.pygame.key.get_pressed = keypress([game.pygame.K_w, game.pygame.K_d])
        car.check_inputs()
        self.assertGreater(car.pos_y, 0, 'W & D input failed!')
        self.assertLess(car.rotation, 180, 'W & D input failed!')

        reset_car(car)
        game.pygame.key.get_pressed = keypress([game.pygame.K_s, game.pygame.K_a])
        car.check_inputs()
        self.assertLess(car.pos_y, 0, 'S & A input failed!')
        self.assertLess(car.rotation, 180, 'S & A input failed!')

        reset_car(car)
        game.pygame.key.get_pressed = keypress([game.pygame.K_s, game.pygame.K_d])
        car.check_inputs()
        self.assertLess(car.pos_y, 0, 'S & D input failed!')
        self.assertGreater(car.rotation, 180, 'S & D input failed!')

        reset_car(car)
        game.pygame.key.get_pressed = keypress([game.pygame.K_w, game.pygame.K_s])
        car.check_inputs()
        self.assertEqual(car.pos_y, 0, 'W & S input failed!')

        car._allow_forwards = False
        game.pygame.key.get_pressed = keypress(game.pygame.K_w)
        car.check_inputs()
        self.assertEqual(car.pos_y, 0, 'Locking forwards failed!')
        car._allow_forwards = True

        car._allow_reverse = False
        game.pygame.key.get_pressed = keypress(game.pygame.K_s)
        car.check_inputs()
        self.assertEqual(car.pos_y, 0, 'Locking reverse failed!')
        car._allow_reverse = True

    def test_powerups(self):
        car.damage = 1
        car.power_up('repair')
        self.assertEqual(car.damage, 0, 'Repair powerup failed!')

        car._boost_timeout = 0
        car.power_up('boost')
        self.assertTrue(car._boost_timeout, 'Boost powerup failed!')
        self.assertEqual(car._move_speed, 10 + game.global_car_move_speed, 'Boost move speed failed!')
        self.assertEqual(car._rotation_speed, 5 + game.global_car_rotation_speed, 'Boost rotation speed failed!')

        car.power_up('bullet')
        self.assertEqual(car.damage, car.durability, 'Bullet powerup failed!')


class TestNpcCar(unittest.TestCase):
    def test_move_speed(self):
        speed = npc.move_speed - game.global_car_move_speed
        npc.set_move_speed(7)
        self.assertEqual(npc.move_speed - game.global_car_move_speed, 7, 'Npc move speed failed!')
        npc.set_move_speed(speed)

    def test_rotation_speed(self):
        speed = npc.rotation_speed - game.global_car_rotation_speed
        npc.set_rotation_speed(7)
        self.assertEqual(npc.rotation_speed - game.global_car_rotation_speed, 7, 'Npc rotation speed failed!')
        npc.set_rotation_speed(speed)

    def test_check_laps(self):
        reset_car(npc)
        npc.check_laps(game.pygame.rect.Rect(0, 0, npc.rect.width, npc.rect.height),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide lap
        self.assertTrue(npc.lap_collision, 'Lap collision failed!')
        self.assertEqual(npc.laps, 1, 'Initial lap failed!')
        npc.check_laps(game.pygame.rect.Rect(0, 0, npc.rect.width, npc.rect.height),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide lap
        self.assertEqual(npc.laps, 1, 'Lap incremented twice!')
        npc.check_laps(game.pygame.rect.Rect(100, 100, 1, 1),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide none
        self.assertFalse(npc.lap_collision, "Lap collision didn't reset!")
        npc.check_laps(game.pygame.rect.Rect(200, 200, 1, 1),  # Collide halfway
                       game.pygame.rect.Rect(0, 0, npc.rect.width, npc.rect.height))
        self.assertTrue(npc.lap_collision, 'Lap collision failed!')
        self.assertTrue(npc.lap_halfway, 'Lap halfway failed!')
        self.assertEqual(npc.laps, 1, 'Lap increased on halfway trigger!')
        npc.check_laps(game.pygame.rect.Rect(100, 100, 1, 1),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide none
        self.assertFalse(npc.lap_collision, "Lap collision didn't reset on halfway!")
        npc.check_laps(game.pygame.rect.Rect(0, 0, npc.rect.width, npc.rect.height),
                       game.pygame.rect.Rect(200, 200, 1, 1))  # Collide lap
        self.assertFalse(npc.lap_halfway, "Lap halfway didn't reset!")
        self.assertEqual(npc.laps, 2, 'Lap increase failed!')

    def test_check_checkpoints(self):
        reset_car(npc)
        game.checkpoint_triggers = [[], []]
        npc.checkpoint_collision = False
        npc.check_checkpoints([game.pygame.rect.Rect(0, 0, npc.rect.width, npc.rect.height)])
        self.assertTrue(npc.checkpoint_collision, 'Checkpoint trigger failed!')
        self.assertTrue(npc.point_checked, 'Checkpoint trigger failed!')
        self.assertIn([npc.name, npc.laps, npc.image_dir], game.checkpoint_triggers[0], 'Checkpoint trigger failed!')
        npc.check_checkpoints([game.pygame.rect.Rect(0, 0, npc.rect.width, npc.rect.height)])
        self.assertNotIn([npc.name, npc.laps, npc.image_dir], game.checkpoint_triggers[1], 'Checkpoint added twice!')
        npc.check_checkpoints([game.pygame.rect.Rect(100, 100, 1, 1)])
        self.assertFalse(npc.checkpoint_collision, 'Checkpoint reset failed!')
        self.assertFalse(npc.point_checked, 'Checkpoint reset failed!')

    def test_clear_checkpoints(self):
        npc.check_checkpoints([game.pygame.rect.Rect(0, 0, npc.rect.width, npc.rect.height)])
        npc.clear_checkpoints()
        self.assertNotIn([npc.name, npc.laps, npc.image_dir], game.checkpoint_triggers[0], 'Clear checkpoints failed!')

    def test_car_collision(self):
        reset_car(npc)
        reset_car(car_2)
        npc.check_car_collision(car_2)
        self.assertEqual(npc.collision, car_2, 'Car collision failed!')
        car_2.move(100, 0)
        npc.check_car_collision(car_2)
        self.assertFalse(npc.collision, 'Car collision did not reset!')
        car_2.move(0, npc.rect.height-2)
        npc.check_car_collision(car_2)
        self.assertFalse(npc.allow_forwards, 'Front collision did not stop!')
        self.assertTrue(npc.allow_reverse, 'Front collision did not stop!')
        car_2.move(0, -npc.rect.height+2)
        npc.check_car_collision(car_2)
        self.assertFalse(npc.allow_reverse, 'Rear collision did not stop!')
        self.assertTrue(npc.allow_forwards, 'Rear collision did not stop!')

    def test_follow_path(self):
        npc.allow_forwards = True
        npc.allow_reverse = True
        reset_car(npc)
        npc.path = [[0], [0]]
        npc.follow_path()  # Move forwards
        self.assertGreater(npc.pos_y, 0, 'Path forwards failed!')

        reset_car(npc)
        npc.path = [[0, 2], [0, 2]]
        npc.follow_path()
        self.assertGreater(npc.pos_y, 0, 'Path forwards left failed! (movement')
        self.assertGreater(npc.rotation, 180, 'Path forwards left failed! (rotation)')

        reset_car(npc)
        npc.path = [[0, 3], [0, 3]]
        npc.follow_path()
        self.assertGreater(npc.pos_y, 0, 'Path forwards right failed! (movement)')
        self.assertGreater(npc.rotation, 180, 'Path forwards right failed! (rotation)')

    def test_power_up(self):
        npc.collision = False
        npc.penalty_time = False
        npc.power_up('lightning')
        self.assertEqual(npc.lightning_animation, game.pygame.time.get_ticks() // 70, 'Lightning power-up failed!')