from pico2d import *

class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 30)
        self.image.draw(1200, 30)
        draw_rectangle(*self.get_bb())# *가 튜플을 풀어 헤칠 수 있음 원래 4개의 튜플이 1개로 오지만 이걸로 4개 각각으로 온다.

    def get_bb(self):
        return 0, 0, 1600, 50

    def handle_collision(self, group, other):
        # if group == 'grass:ball':

        pass

