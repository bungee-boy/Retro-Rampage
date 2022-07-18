import unittest
import main as game

car = game.Car(game.Player(1))
npc = game.NPCCar(1, game.RED_CAR, (40, 70), 'npc', 'racetrack', 1)


class TestCar(unittest.TestCase):
    def test_rotation(self):
        car.rotate(2)
        self.assertEqual(car.rotation, 0, 'Snapping to 0 from 2 failed!')
        car.rotate(358)
        self.assertEqual(car.rotation, 0, 'Snapping to 0 from 358 failed!')
        car.rotate(92)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 92 failed!')
        car.rotate(88)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 88 failed!')

    def test_movement(self):
        car.move(0, 0)
        self.assertTupleEqual(car.rect.center, (0, 0), 'Failed to move to 0, 0!')
        car.move(100, 0)
        self.assertTupleEqual(car.rect.center, (100, 0), 'Failed to move to 100, 0!')
        car.move(0, 100)
        self.assertTupleEqual(car.rect.center, (0, 100), 'Failed to move to 0, 100!')

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
        npc.move(0, 0)  # Position top left facing down
        npc.rotate(180)
        npc.path = [[0], [0]]
        npc.update()  # Move forwards
        self.assertGreater(npc.pos_y, 0, 'Path reverse failed!')
        npc.path = [[1], [1]]
        npc.update()  # Move backwards
        self.assertEqual(npc.pos_y, 0, 'Path forwards failed!')
        npc.path = [[0, 2], [0, 2]]
        npc.update()
        self.assertGreater(npc.pos_y, 0, 'Path forwards left failed!')
        self.assertGreater(npc.rotation, 180, 'Path forwards left failed!')
        npc.path = [[1, 2], [1, 2]]
        npc.update()
        self.assertEqual(npc.pos_y, 0, 'Path backwards left failed!')
        self.assertEqual(npc.rotation, 180, 'Path backwards left failed!')
        npc.path = [[0, 3], [0, 3]]
        npc.update()
        self.assertGreater(npc.pos_y, 0, 'Path forwards right failed!')
        self.assertLess(npc.rotation, 180, 'Path forwards right failed!')
        npc.path = [[1, 3], [1, 3]]
        npc.update()
        self.assertEqual(npc.pos_y, 0, 'Path backwards right failed!')
        self.assertEqual(npc.roation, 180, 'Path backwards right failed!')

