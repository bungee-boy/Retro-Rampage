import unittest
import main as game

game.Player_amount = 2
game.Npc_amount = 1
game.Players = [game.Player(0), game.Player(1)]
car = game.Car(game.Players[0])
car_2 = game.Car(game.Players[1])
npc = game.NpcCar(game.Player(2, is_player=False))


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
    # def test_self(self):
    #    self.assertEqual(keypress())

    def test_load_defaults(self):
        game.controls = []
        player = game.Player(0)
        self.assertEqual(player.id, 0)
        self.assertEqual(player.veh_name, 'Family Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.RED_CAR, 'Loading player defaults failed!')
        self.assertEqual(player.controls, 'wasd', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, player.id + 1, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(1)
        self.assertEqual(player.id, 1)
        self.assertEqual(player.veh_name, 'Sports Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.YELLOW_CAR, 'Loading player defaults failed!')
        self.assertEqual(player.controls, 'arrows', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, player.id + 1, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(2)
        self.assertEqual(player.id, 2)
        self.assertEqual(player.veh_name, 'Luxury Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.GREEN_CAR, 'Loading player defaults failed!')
        self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, player.id + 1, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(3)
        self.assertEqual(player.id, 3)
        self.assertEqual(player.veh_name, 'Truck', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.BLUE_CAR, 'Loading player defaults failed!')
        self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, player.id + 1, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(4)
        self.assertEqual(player.id, 4)
        self.assertEqual(player.veh_name, 'Race Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.BLACK_CAR, 'Loading player defaults failed!')
        self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, player.id + 1, 'Loading player defaults failed!')
        self.assertEqual(player.default_controls, player.controls, 'Loading player defaults failed!')

        player = game.Player(5)
        self.assertEqual(player.id, 5)
        self.assertEqual(player.veh_name, 'Family Car', 'Loading player defaults failed!')
        self.assertEqual(player.veh_colour, game.RED_CAR, 'Loading player defaults failed!')
        self.assertEqual(player.controls, 'controller', 'Loading player defaults failed!')
        self.assertEqual(player.name, '', 'Loading player defaults failed!')
        self.assertEqual(player.start_pos, player.id + 1, 'Loading player defaults failed!')
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
        self.assertEqual(car.rotation, 360, 'Snapping to 360 from 2 failed!')
        car.rotate(358)
        self.assertEqual(car.rotation, 0, 'Snapping to 0 from 358 failed!')
        car.rotate(92)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 92 failed!')
        car.rotate(88)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 88 failed!')

    def test_set_controls(self):
        car.set_controls('wasd')
        self.assertEqual(car.input_type, 'wasd', 'Keyboard control failed!')
        self.assertEqual(car._up, game.pygame.K_w, 'W key control failed!')
        self.assertEqual(car._down, game.pygame.K_s, 'S key control failed!')
        self.assertEqual(car._left, game.pygame.K_a, 'A key control failed!')
        self.assertEqual(car._right, game.pygame.K_d, 'D key control failed!')

        car.set_controls('arrows')
        self.assertEqual(car.input_type, 'arrows', 'Keyboard control failed!')
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
            except game.pygame.log_err:
                print('\n** Connect a controller to run controller tests **')
        else:
            print('\n** Run tests on windows to check controller inputs **')

    def test_checkpoints(self):
        points = [game.pygame.rect.Rect(0, 20, 10, 10),
                  game.pygame.rect.Rect(0, 40, 10, 10), game.pygame.rect.Rect(0, 60, 10, 10)]
        reset_car(car)
        car.checkpoint_count = 0
        car.checkpoint_time = 0
        car.finished = True
        car.check_checkpoints(points)
        self.assertEqual(car.checkpoint_count + car.checkpoint_time, 0, 'Checkpoint triggered after finish!')
        car.finished = False
        car.move(0, 0)
        car.check_checkpoint(points)
        self.assertEqual(car.checkpoint_time, game.pygame.get_ticks(), 'Checkpoint did not trigger!')
        self.assertEqual(car.checkpoint_count, 1, 'Checkpoint did not trigger!')
        car.move(0, 20)
        car.check_checkpoints(points)

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
        game.Track_mask = mask
        car.check_track_collisions()
        self.assertEqual(car.collision, 'track', 'Track collision failed!')
        self.assertTrue(car._collision_sound, 'Track collision failed!')
        self.assertEqual(car.damage, 1, 'Track collision failed!')
        car.check_track_collisions()
        self.assertEqual(car.damage, 1, 'Track collision triggered twice!')
        car.move(200, 200)
        car.check_track_collisions()
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

        game.pygame.key.get_pressed = keypress([])

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
        speed = npc._move_speed - game.global_car_move_speed
        npc.set_move_speed(7)
        self.assertEqual(npc._move_speed - game.global_car_move_speed, 7, 'Npc move speed failed!')
        npc.set_move_speed(speed)

    def test_rotation_speed(self):
        speed = npc._rotation_speed - game.global_car_rotation_speed
        npc.set_rotation_speed(7)
        self.assertEqual(npc._rotation_speed - game.global_car_rotation_speed, 7, 'Npc rotation speed failed!')
        npc.set_rotation_speed(speed)

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
        self.assertFalse(npc.allow_forward, 'Front collision did not stop!')
        self.assertTrue(npc.allow_back, 'Front collision did not stop!')
        car_2.move(0, -npc.rect.height+2)
        npc.check_car_collision(car_2)
        self.assertFalse(npc.allow_back, 'Rear collision did not stop!')
        self.assertTrue(npc.allow_forward, 'Rear collision did not stop!')

    def test_power_up(self):
        npc.collision = False
        npc.penalty_time = False
        npc.power_up('lightning')
        self.assertEqual(npc.lightning_animation, game.pygame.time.get_ticks() // 70, 'Lightning power-up failed!')
