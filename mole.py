from pico2d import load_image, clamp, get_time
import random
import math

class Mole:
    def __init__(self, x, y, speed):
        self.x, self.y = x, y
        self.speed = speed
        self.visible = True
        self.image = load_image('mole.png')
        self.attack_image = load_image('mole_Attack.png')
        self.state = 'wander'
        self.wander_timer = random.randint(50, 150)
        self.dir_x = random.choice([-1, 1])
        self.face_dir = 1

        # 애니메이션 관련 변수
        self.frame = 0
        self.last_time = get_time()
        self.anim_acc = 0.0

        # Wander 애니메이션 속성
        self.wander_anim_delay = 0.15
        self.wander_frame_width = 28
        self.wander_frame_height = 18
        self.wander_frame_count = 3

        # Attack 애니메이션 속성
        self.attack_anim_delay = 0.1
        self.attack_frame_width = 29  # 145 / 5
        self.attack_frame_height = 25
        self.attack_frame_count = 5


    def update(self, character):
        if not self.visible:
            return

        # 상태 결정
        distance_to_character = abs(self.x - character.x)
        new_state = self.state
        if distance_to_character < 100:
            new_state = 'attack'
        else:
            new_state = 'wander'

        # 상태가 변경되면 프레임 초기화
        if self.state != new_state:
            self.state = new_state
            self.frame = 0
            self.anim_acc = 0.0

        # 현재 상태에 맞는 애니메이션 속성 가져오기
        if self.state == 'attack':
            anim_delay = self.attack_anim_delay
            frame_count = self.attack_frame_count
        else: # wander
            anim_delay = self.wander_anim_delay
            frame_count = self.wander_frame_count

        # 애니메이션 업데이트
        now = get_time()
        dt = now - self.last_time
        self.last_time = now
        self.anim_acc += dt
        if self.anim_acc >= anim_delay:
            steps = int(self.anim_acc // anim_delay)
            self.anim_acc -= steps * anim_delay
            self.frame = (self.frame + steps) % frame_count

        # 상태에 따른 행동 실행
        if self.state == 'wander':
            self.wander()
        elif self.state == 'attack':
            self.attack(character)

    def wander(self):
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.dir_x = random.choice([-1, 0, 1])
            self.wander_timer = random.randint(50, 150)

        if self.dir_x != 0:
            self.face_dir = self.dir_x

        self.x += self.dir_x * self.speed
        # 화면 경계 처리
        self.x = clamp(50, self.x, 1150)

    def attack(self, character):
        # 공격 상태에서는 움직이지 않음
        # 캐릭터 방향을 바라보도록 face_dir 설정
        if character.x > self.x:
            self.face_dir = 1
        else:
            self.face_dir = -1

    def draw(self):
        if self.visible:
            if self.state == 'attack':
                frame_x = self.frame * self.attack_frame_width
                if self.face_dir == -1:
                    self.attack_image.clip_draw(frame_x, 0, self.attack_frame_width, self.attack_frame_height, self.x, self.y, self.attack_frame_width * 3, self.attack_frame_height * 3)
                else:
                    self.attack_image.clip_composite_draw(frame_x, 0, self.attack_frame_width, self.attack_frame_height, 0, 'h', self.x, self.y, self.attack_frame_width * 3, self.attack_frame_height * 3)
            else: # wander
                frame_x = self.frame * self.wander_frame_width
                if self.face_dir == -1: # 왼쪽을 볼 때
                    self.image.clip_draw(frame_x, 0, self.wander_frame_width, self.wander_frame_height, self.x, self.y, self.wander_frame_width * 3, self.wander_frame_height * 3)
                else: # 오른쪽을 볼 때
                    self.image.clip_composite_draw(frame_x, 0, self.wander_frame_width, self.wander_frame_height, 0, 'h', self.x, self.y, self.wander_frame_width * 3, self.wander_frame_height * 3)

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True