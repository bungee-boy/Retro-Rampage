import unittest

import main as game

car = game.Car(game.Player(1))


class TestCar(unittest.TestCase):
    def test_car_rotation(self):
        car.rotate(2)
        self.assertEqual(car.rotation, 0, 'Snapping to 0 from 2 failed!')
        car.rotate(358)
        self.assertEqual(car.rotation, 0, 'Snapping to 0 from 358 failed!')
        car.rotate(92)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 92 failed!')
        car.rotate(88)
        self.assertEqual(car.rotation, 90, 'Snapping to 90 from 88 failed!')

    def test_car_movement(self):
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

        self.controller = pyvjoy.VJoyDevice(0)
        game.controllers.append(self.controller)  # Connect dummy controller
        car.set_controls(self.controller)  # Bind car to dummy controller
        self.assertEqual(car.controller, self.controller, 'Binding controller failed!')
