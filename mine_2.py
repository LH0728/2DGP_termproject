from pico2d import *
import random

class Mine_2:
    def __init__(self):
        self.image = load_image('bg4_finish.png')

    def draw(self):
        self.image.draw(600, 400, 1200, 800)

    def update(self, character):
        pass