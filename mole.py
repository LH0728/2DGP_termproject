from pico2d import load_image, clamp, get_time
import random
import math

class Mole:
    def __init__(self, x, y, speed):
        self.x, self.y = x, y
        self.speed = speed
        self.visible = True
        self.image = load_image('mole.png')
        self.state = 'wander'
        self.wander_timer = random.randint(50, 150)
        self.dir_x = random.choice([-1, 1])
        self.face_dir = 1

        # 애니메이션 관련 변수
        self.frame = 0
        self.last_time = get_time()
        self.anim_acc = 0.0
        self.anim_delay = 0.15
        self.frame_width = 28
        self.frame_height = 18
        self.frame_count = 3

    def update(self, character):
        if not self.visible:
            return

        # 애니메이션 업데이트
        now = get_time()
        dt = now - self.last_time
        self.last_time = now
        self.anim_acc += dt
        if self.anim_acc >= self.anim_delay:
            steps = int(self.anim_acc // self.anim_delay)
            self.anim_acc -= steps * self.anim_delay
            self.frame = (self.frame + steps) % self.frame_count

        distance_to_character = math.sqrt((self.x - character.x)**2 + (self.y - character.y)**2)

        if distance_to_character < 30:
            self.state = 'chase'
        else:
            self.state = 'wander'

        if self.state == 'wander':
            self.wander()
        elif self.state == 'chase':
            self.chase(character)

        # 화면 경계 처리
        self.x = clamp(50, self.x, 1150)


    def wander(self):
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.dir_x = random.choice([-1, 0, 1])
            self.wander_timer = random.randint(50, 150)

        if self.dir_x != 0:
            self.face_dir = self.dir_x

        self.x += self.dir_x * self.speed

    def chase(self, character):
        dx = character.x - self.x
        dist = abs(dx)
        if dist > 0:
            move_x = (dx / dist) * self.speed * 1.5
            self.x += move_x

            if move_x > 0:
                self.face_dir = 1
            elif move_x < 0:
                self.face_dir = -1

    def draw(self):
        if self.visible:
            frame_x = self.frame * self.frame_width
            if self.face_dir == -1: # 왼쪽을 볼 때
                self.image.clip_draw(frame_x, 0, self.frame_width, self.frame_height, self.x, self.y, self.frame_width * 3, self.frame_height * 3)
            else: # 오른쪽을 볼 때
                self.image.clip_composite_draw(frame_x, 0, self.frame_width, self.frame_height, 0, 'h', self.x, self.y, self.frame_width * 3, self.frame_height * 3)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True