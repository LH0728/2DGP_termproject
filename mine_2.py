from pico2d import *
import random
import math


class Mine_2:
    def __init__(self):
        self.soil_width, self.soil_height = 60, 60
        self.bg_y = 400
        self.image = load_image('bg4_finish.png')
        self.image2 = load_image('bg1_loop.png')
        # Soil 객체를 담을 리스트 생성
        self.soils = []
        self.Minerals = []
        # Soil 객체의 생성 간격을 실제 크기인 60x60으로 수정합니다.
        soil_width, soil_height = 60, 60
        # y좌표 0부터 150까지, x좌표 0부터 1200까지 Soil 객체로 채우기
        for y in range(0, 150, soil_height):
            for x in range(0, 1200, soil_width):
                self.soils.append(Soil(x + soil_width // 2, y + soil_height // 2))
        self.lowest_generated_y = 0

    def draw(self, camera_y):
        if camera_y > -800:
            self.image.draw(600, 400 - camera_y, 1200, 800)

        screen_bottom_y = camera_y

        if screen_bottom_y < 0:
            loop_h = self.image2.h

            screen_top_y = camera_y + 800
            visible_top = min(0, screen_top_y)

            start_depth = -visible_top
            end_depth = -screen_bottom_y

            start_idx = int(start_depth // loop_h)
            end_idx = int(end_depth // loop_h) + 1

            for i in range(start_idx, end_idx + 1):

                world_y = - (i * loop_h) - (loop_h // 2)

                draw_y = world_y - camera_y
                self.image2.draw(600, draw_y, 1200, loop_h)

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
        screen_bottom_y = camera_y

        while screen_bottom_y < self.lowest_generated_y:
            new_row_y = self.lowest_generated_y - (self.soil_height // 2)
            self.generate_new_row(new_row_y)
            self.lowest_generated_y -= self.soil_height

        # 배경 스크롤 관련 보정 (이 부분도 유지)
        if (self.bg_y - 400) - camera_y > 800:
            self.bg_y -= 800

    def generate_new_row(self, y):
        for x in range(0, 1200, self.soil_width):
            #if random.random() < 0.1:
            #   continue
            self.soils.append(Soil(x + self.soil_width // 2, y))





class Soil:
    # ... (Soil 클래스 원본과 동일 - 수정 없음) ...
    image = None

    def __init__(self, x, y):
        if Soil.image is None:
            Soil.image = load_image('TileCraftGroundSetVersion2.png')
        self.x, self.y = x, y

        self.hp = 2
        self.last_hit_time = 0

    def hit(self):
        now = get_time()

        # [중요] 마지막으로 맞은지 0.5초가 안 지났으면 데미지 무시
        # (한 번 휘두를 때 여러 번 맞는 것 방지)
        if now - self.last_hit_time < 0.5:
            return False

        self.hp -= 1
        self.last_hit_time = now

        if self.hp <= 0:
            return True

        return False  # 아직 안 깨짐
    def draw(self, camera_y):
        draw_y = self.y - camera_y
        self.image.clip_draw(3, self.image.h - 45, 42, 42, self.x, draw_y, 60, 60)
        l, b, r, t = self.get_bb()
        #draw_rectangle(l, b - camera_y, r, t - camera_y)

    def update(self, character):
        pass

    def get_bb(self):
        # 객체의 중심 좌표(self.x, self.y)와 크기(60x60)를 기반으로
        # 왼쪽, 아래, 오른쪽, 위쪽 좌표를 반환합니다.
        return self.x - 30, self.y - 30, self.x + 30, self.y + 30


class Mineral:
    # 이미지를 종류별로 저장할 딕셔너리 (최초 로딩 후 재사용)
    images = {}

    MINERAL_SPEED = 3.0
    MINERAL_RANGE = 8

    def __init__(self, x, y):
        self.x = x
        self.original_y = y - 20
        self.y = y

        # 1번(80), 2번(10), 3번(5), 4번(1)의 가중치를 설정합니다.
        # choices 함수는 weights 비율에 따라 알아서 확률을 계산해줍니다.
        mineral_types = [1, 2, 3, 4]
        weights = [80, 10, 5, 1]

        # k=1은 하나를 뽑겠다는 뜻이며, 리스트로 반환되므로 [0]으로 값을 꺼냅니다.
        self.type = random.choices(mineral_types, weights=weights, k=1)[0]

        # 해당 타입의 이미지가 아직 로딩되지 않았다면 로딩합니다.
        if self.type not in Mineral.images:
            if self.type == 1:
                Mineral.images[1] = load_image('21203.png')  # 80% (기본)
            elif self.type == 2:
                Mineral.images[2] = load_image('21204.png')  # 10%
            elif self.type == 3:
                Mineral.images[3] = load_image('21205.png')  # 5%
            elif self.type == 4:
                Mineral.images[4] = load_image('21206.png')  # 1% (전설)

        # 결정된 이미지를 현재 객체의 이미지로 설정
        self.image = Mineral.images[self.type]
        self.scale = 2.0
    def draw(self, camera_y):
        draw_y = self.y - camera_y
        self.image.clip_draw(
            0, 0, self.image.w, self.image.h,  # Source (원본에서 가져올 영역)
            self.x, draw_y,  # Position (화면에 그릴 위치)
            self.image.w * self.scale, self.image.h * self.scale  # Size (화면에 그려질 크기)
        )
        # l, b, r, t = self.get_bb()
        # draw_rectangle(l, b - camera_y, r, t - camera_y)

    def update(self, character):
        time_based_offset = math.sin(get_time() * Mineral.MINERAL_SPEED + self.x)
        MINERAL_offset = time_based_offset * Mineral.MINERAL_RANGE
        self.y = self.original_y + MINERAL_offset

    def get_bb(self):
        half_width = (self.image.w * self.scale) / 2
        half_height = (self.image.h * self.scale) / 2
        return self.x - half_width, self.y - half_height, self.x + half_width, self.y + half_height