from pico2d import *
import random

class Mine_2:
    def __init__(self):
        self.image = load_image('bg4_finish.png')
        # Soil 객체를 담을 리스트 생성
        self.soils = []
        # Soil 객체의 생성 간격을 실제 크기인 60x60으로 수정합니다.
        soil_width, soil_height = 60, 60
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

        self.image.clip_draw(3, self.image.h - 45, 42, 42, self.x, self.y, 60, 60)
        draw_rectangle(*self.get_bb())

    def update(self, character):
        pass

    def get_bb(self):
        # 객체의 중심 좌표(self.x, self.y)와 크기(60x60)를 기반으로
        # 왼쪽, 아래, 오른쪽, 위쪽 좌표를 반환합니다.
        return self.x - 30, self.y - 30, self.x + 30, self.y + 30