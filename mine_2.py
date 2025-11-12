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

        char_left = character.x - 20
        char_right = character.x + 20


        max_ground_y = 0

        for soil in self.soils:
            s_left, s_bottom, s_right, s_top = soil.get_bb()

            if char_right < s_left or char_left > s_right:
                continue  #

            if s_top <= character.y + 10:
                # 겹치는 블록 중 가장 높은 블록의 윗면(s_top)을 찾음
                max_ground_y = max(max_ground_y, s_top)

        # 계산된 땅 높이를 캐릭터에 적용
        character.ground_y = max_ground_y+50

        # 모든 Soil 객체 업데이트 (원래 코드)
        for soil in self.soils:
            soil.update(character)


class Soil:
    # ... (Soil 클래스 원본과 동일 - 수정 없음) ...
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