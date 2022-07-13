import unittest
import main as game

car = game.Car(game.Player(1))
car_2 = game.Car(game.Player(2))
npc = game.NPCCar(1, game.RED_CAR, (40, 70), 'npc', 'racetrack', 1)


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


def reset_car(vehicle):  # Used to reset the car's position when testing movement
    vehicle.move(0, 0)
    vehicle.rotate(180)


reset_car(car)
reset_car(car_2)


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

        '''
        import platform
        if platform.system() == 'Windows':
            import pyvjoy
            self.v_joystick = pyvjoy.VJoyDevice(1)
            self.v_joystick.set_button(1, 1)

            self.controller = game.pygame.joystick.Joystick(1)
            game.controllers.append(self.controller)  # Connect dummy controller
            car.set_controls(self.controller)  # Bind car to dummy controller
            self.assertEqual(car.controller, self.controller, 'Binding controller failed!')
        else:
            print('\n**Run tests on windows to check controller inputs**\n')
        '''

    def test_laps(self):
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
    def test_path_movement(self):
        reset_car(npc)
        npc.path = [[0], [0]]
        npc.update()  # Move forwards
        self.assertGreater(npc.pos_y, 0, 'Path forwards failed!')

        reset_car(npc)
        npc.path = [[0, 2], [0, 2]]
        npc.update()
        self.assertGreater(npc.pos_y, 0, 'Path forwards left failed! (movement')
        self.assertGreater(npc.rotation, 180, 'Path forwards left failed! (rotation)')

        reset_car(npc)
        npc.path = [[0, 3], [0, 3]]
        npc.update()
        self.assertGreater(npc.pos_y, 0, 'Path forwards right failed! (movement)')
        self.assertGreater(npc.rotation, 180, 'Path forwards right failed! (rotation)')
