from pico2d import load_image, get_time


class Village:
    def __init__(self):
        self.image = load_image('bg_near.png')
        self.image2 = load_image('bg_tower.png')
        self.image3 = load_image('grass.png')

        # 배경 이미지를 그릴 x 좌표들 (캐릭터 y축 150에 맞춰서)
        self.copy_x_positions = [0, 300, 600, 900, 1200]

        # image3를 image2 아래 빈 공간에 깔 x 좌표들
        self.ground_x_positions = [150, 450, 750, 1050]

    def draw(self, camera_y):
        # image3를 image2 아래쪽 빈 공간에 쭉 깔기 (y=100 아래 공간)
        for x_pos in self.ground_x_positions:
            self.image3.draw(x_pos, 50, 300, 115)

        self.image2.draw_to_origin(0, 100, 1200, 800)

        # image2 바로 위에 딱 붙여서 그리기 (y=100이 바닥이므로 그 위에 배치)
        for x_pos in self.copy_x_positions:
            self.image.draw(x_pos, 200, 300, 200)

    def update(self):
        pass

class Merchant:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = load_image('10201_T1.png')

        self.frame = 0
        self.timer = 0.0
        self.frame_count = 4
        self.anim_speed = 0.2
        self.width = self.image.w // self.frame_count
        self.height = self.image.h
        self.last_time = get_time()


    def update(self):

        now = get_time()
        dt = now - self.last_time
        self.last_time = now


        self.timer += dt
        if self.timer >= self.anim_speed:
            self.timer = 0
            self.frame = (self.frame + 1) % self.frame_count

    def draw(self, camera_y):
        draw_y = self.y - camera_y
        self.image.clip_draw(
            self.frame * self.width, 0, self.width, self.height,
            self.x, draw_y, 150, 150
        )