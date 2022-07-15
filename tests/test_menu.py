import unittest
import main as game


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
