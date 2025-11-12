from pico2d import *
from mole import Mole
import random

class Mine:
    def __init__(self):
        # 'bg_near.png'를 광산 배경 이미지로 사용합니다.
        # 다른 이미지를 원하시면 파일명을 수정해주세요.
        self.image = load_image('bg4_finish.png')
        self.moles = [Mole(random.randint(100, 1100), 120, 2) for _ in range(5)]

    def draw(self):
        # 이미지를 화면 중앙에 꽉 채워서 그립니다.
        self.image.draw(600, 400, 1200, 800)
        for mole in self.moles:
            mole.draw()

    def update(self, character):
        # 배경은 특별히 업데이트할 내용이 없습니다.
        for mole in self.moles:
            mole.update(character)
