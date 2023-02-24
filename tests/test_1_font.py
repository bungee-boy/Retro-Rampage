import unittest
import main as game


class TestLibrary(unittest.TestCase):
    def test_font_loader(self):
        err_msg = 'Font loader test failed!'
        self.assertEqual(game.fonts.load(bar=True), game.fonts.assets + 'default.ttf', err_msg)
        self.assertEqual(game.fonts.load(), game.fonts.assets + 'no_bar.ttf', err_msg)
        self.assertEqual(game.fonts.load(bar=True, three_d=True),
                         game.fonts.assets + '3D.ttf', err_msg)
        self.assertEqual(game.fonts.load(bold=True), game.fonts.assets + 'no_bar_bold.ttf', err_msg)
