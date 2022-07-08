import unittest
from main import Car, Player

car = Car(Player(1))


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


