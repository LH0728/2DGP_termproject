from pico2d import *
import random

class Mine_2:
    def __init__(self):
        self.image = load_image('bg4_finish.png')
        # Soil 객체를 담을 리스트 생성
        self.soils = []
        # Mining_1_1.png 이미지 크기를 49x49로 변경
        soil_width, soil_height = 48, 49
        # y좌표 0부터 150까지, x좌표 0부터 1200까지 Soil 객체로 채우기
        for y in range(0, 150, soil_height):
            for x in range(0, 1200, soil_width):
                self.soils.append(Soil(x + soil_width // 2, y + soil_height // 2))


    def draw(self):
        self.image.draw(600, 400, 1200, 800)
        # 모든 Soil 객체 그리기
        for soil in self.soils:
            soil.draw()

    def update(self, character):
        # 모든 Soil 객체 업데이트
        for soil in self.soils:
            soil.update(character)

class Soil:
    image = None
    def __init__(self, x, y):
        if Soil.image is None:
            Soil.image = load_image('TileCraftGroundSetVersion2.png')
        self.x, self.y = x, y

    def draw(self):
        # 이미지의 왼쪽 위 (0, 0) 위치에서 49x49 크기로 잘라내어 그립니다.
        # clip_draw의 y좌표는 이미지의 하단을 기준으로 하므로, 이미지 높이에서 49를 빼줍니다.
        self.image.clip_draw(0, self.image.h - 49, 49, 49, self.x, self.y, 60, 60)

    def update(self, character):
        pass