from pico2d import *
import random


class Mine_2:
    def __init__(self):
        self.soil_width, self.soil_height = 60, 60
        self.bg_y = 400
        self.image = load_image('bg4_finish.png')
        # Soil 객체를 담을 리스트 생성
        self.soils = []
        # Soil 객체의 생성 간격을 실제 크기인 60x60으로 수정합니다.
        soil_width, soil_height = 60, 60
        # y좌표 0부터 150까지, x좌표 0부터 1200까지 Soil 객체로 채우기
        for y in range(0, 150, soil_height):
            for x in range(0, 1200, soil_width):
                self.soils.append(Soil(x + soil_width // 2, y + soil_height // 2))
        self.lowest_generated_y = 0

    def draw(self, camera_y):
        draw_bg_y_1 = self.bg_y - camera_y
        draw_bg_y_2 = self.bg_y - 800 - camera_y  # 800px 아래에 다음 배경

        self.image.draw(600, draw_bg_y_1, 1200, 800)
        self.image.draw(600, draw_bg_y_2, 1200, 800)

        for soil in self.soils:
            soil.draw(camera_y)

    def update(self, character):
        char_left = character.x - 20
        char_right = character.x + 20

        max_ground_y = -999999

        for soil in self.soils:
            s_left, s_bottom, s_right, s_top = soil.get_bb()

            if s_right < char_left or s_left > char_right:
                continue

            if s_top < character.y:
                max_ground_y = max(max_ground_y, s_top)

        character.ground_y = max_ground_y+50

    def procedural_update(self, camera_y):
        screen_top_y = camera_y + 800
        self.soils = [soil for soil in self.soils if soil.get_bb()[1] < screen_top_y]

        screen_bottom_y = camera_y

        while screen_bottom_y < self.lowest_generated_y:
            new_row_y = self.lowest_generated_y - (self.soil_height // 2)
            self.generate_new_row(new_row_y)
            self.lowest_generated_y -= self.soil_height


        if (self.bg_y - 400) - camera_y > 800:
            self.bg_y -= 800

    def generate_new_row(self, y):
        for x in range(0, 1200, self.soil_width):
            if random.random() < 0.1:
                continue
            self.soils.append(Soil(x + self.soil_width // 2, y))





class Soil:
    # ... (Soil 클래스 원본과 동일 - 수정 없음) ...
    image = None

    def __init__(self, x, y):
        if Soil.image is None:
            Soil.image = load_image('TileCraftGroundSetVersion2.png')
        self.x, self.y = x, y

    def draw(self, camera_y):
        draw_y = self.y - camera_y
        self.image.clip_draw(3, self.image.h - 45, 42, 42, self.x, draw_y, 60, 60)
        l, b, r, t = self.get_bb()
        draw_rectangle(l, b - camera_y, r, t - camera_y)

    def update(self, character):
        pass

    def get_bb(self):
        # 객체의 중심 좌표(self.x, self.y)와 크기(60x60)를 기반으로
        # 왼쪽, 아래, 오른쪽, 위쪽 좌표를 반환합니다.
        return self.x - 30, self.y - 30, self.x + 30, self.y + 30