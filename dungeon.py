# [dungeon.py]
from pico2d import *
import random
import math
from state_machine import StateMachine


# --- 이벤트 확인 함수 ---
def near_player(e):
    return e[0] == 'NEAR_PLAYER'


def animation_end(e):
    return e[0] == 'ANIMATION_END'


# --- 고블린 상태 클래스: 이동 (Run) ---
class GoblinRun:
    def __init__(self, goblin):
        self.goblin = goblin
        self.frame = 0
        self.action_time = 0.0
        # 60021_1.png는 124x35를 4개로 나눔
        self.frame_count = 4
        # 이동 속도 (초당 픽셀)
        self.speed = 120

    def enter(self, e):
        self.frame = 0
        self.action_time = 0.0

    def do(self, player):
        # 플레이어 방향 계산
        dx = player.x - self.goblin.x

        # 플레이어와 너무 가까우면 떨림 방지를 위해 이동 멈춤
        if abs(dx) > 10:
            # 진행 방향 설정 (1: 오른쪽, -1: 왼쪽)
            self.goblin.face_dir = 1 if dx > 0 else -1
            self.goblin.x += self.goblin.face_dir * self.speed * self.goblin.dt

        # 애니메이션 프레임 업데이트 (약 10 FPS)
        self.action_time += self.goblin.dt
        self.frame = int(self.action_time * 10) % self.frame_count

        # 플레이어와의 거리 계산 및 공격 상태 전환 체크
        distance = math.sqrt((player.x - self.goblin.x) ** 2 + (player.y - self.goblin.y) ** 2)
        if distance < self.goblin.ATTACK_RANGE:
            # ATTACK_RANGE 안으로 들어오면 'NEAR_PLAYER' 이벤트 발생
            self.goblin.state_machine.handle_state_event(('NEAR_PLAYER', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        draw_y = self.goblin.y - camera_y
        frame_width = self.goblin.run_img_w // self.frame_count
        frame_height = self.goblin.run_img_h
        draw_w = frame_width * self.goblin.SCALE
        draw_h = frame_height * self.goblin.SCALE

        # [수정] 원본 이미지가 왼쪽을 보고 있으므로 로직 반전
        if self.goblin.face_dir == -1:  # 왼쪽 이동 (원본 방향)
            self.goblin.image_run.clip_draw(self.frame * frame_width, 0, frame_width, frame_height, self.goblin.x,
                                            draw_y, draw_w, draw_h)
        else:  # 오른쪽 이동 (좌우 반전 필요)
            self.goblin.image_run.clip_composite_draw(self.frame * frame_width, 0, frame_width, frame_height, 0, 'h',
                                                      self.goblin.x, draw_y, draw_w, draw_h)


# --- 고블린 상태 클래스: 공격 (Attack) ---
class GoblinAttack:
    def __init__(self, goblin):
        self.goblin = goblin
        self.frame = 0
        self.action_time = 0.0
        # 60021_1_Attack.png는 204x39를 6개로 나눔
        self.frame_count = 6

    def enter(self, e):
        self.frame = 0
        self.action_time = 0.0

    def do(self, player):
        # 공격 애니메이션 재생
        self.action_time += self.goblin.dt
        self.frame = int(self.action_time * 10)  # 약 10 FPS

        # 애니메이션이 끝나면 'ANIMATION_END' 이벤트 발생 -> 다시 Run 상태로
        if self.frame >= self.frame_count:
            self.goblin.state_machine.handle_state_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        draw_y = self.goblin.y - camera_y
        frame_width = self.goblin.attack_img_w // self.frame_count
        frame_height = self.goblin.attack_img_h
        draw_w = frame_width * self.goblin.SCALE
        draw_h = frame_height * self.goblin.SCALE

        # [수정] 원본 이미지가 왼쪽을 보고 있으므로 로직 반전
        if self.goblin.face_dir == -1:  # 왼쪽 공격 (원본 방향)
            self.goblin.image_attack.clip_draw(self.frame * frame_width, 0, frame_width, frame_height, self.goblin.x,
                                               draw_y, draw_w, draw_h)
        else:  # 오른쪽 공격 (좌우 반전 필요)
            self.goblin.image_attack.clip_composite_draw(self.frame * frame_width, 0, frame_width, frame_height, 0, 'h',
                                                         self.goblin.x, draw_y, draw_w, draw_h)


# --- 고블린 클래스 ---
class Goblin:
    image_run = None
    run_img_w = 0
    run_img_h = 0
    image_attack = None
    attack_img_w = 0
    attack_img_h = 0

    ATTACK_RANGE = 80  # 공격 범위 (픽셀 단위)
    SCALE = 3.0  # 이미지 확대 비율

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp = 3  # 고블린 체력
        self.face_dir = -1  # [수정] 초기 방향 왼쪽으로 설정 (이미지에 맞춤)

        # 프레임 간 시간 계산을 위한 변수
        self.last_time = get_time()
        self.dt = 0.0

        # 이미지 로드 및 크기 정보 저장
        if Goblin.image_run is None:
            Goblin.image_run = load_image('60021_1.png')
            Goblin.run_img_w = Goblin.image_run.w
            Goblin.run_img_h = Goblin.image_run.h

        if Goblin.image_attack is None:
            Goblin.image_attack = load_image('60021_1_attack.png')
            Goblin.attack_img_w = Goblin.image_attack.w
            Goblin.attack_img_h = Goblin.image_attack.h

        # 상태 객체 생성
        self.run_state = GoblinRun(self)
        self.attack_state = GoblinAttack(self)

        # 상태 머신 설정
        self.state_machine = StateMachine(self.run_state, {
            self.run_state: {near_player: self.attack_state},
            self.attack_state: {animation_end: self.run_state}
        })

    def update(self, player):
        now = get_time()
        self.dt = now - self.last_time
        self.last_time = now

        self.state_machine.cur_state.do(player)

    def draw(self, camera_y):
        self.state_machine.draw(camera_y)

    def get_bb(self):
        return self.x - 30, self.y - 40, self.x + 30, self.y + 40

    def hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            return True
        return False


# --- Dungeon 클래스 ---
class Dungeon:
    def __init__(self):
        self.image = load_image('bg6_boss.png')
        self.goblins = []

        # 초기 고블린 스폰
        for _ in range(3):
            self.spawn_goblin()

        self.spawn_timer = 0.0
        self.last_spawn_time = get_time()

    def spawn_goblin(self):
        spawn_side = random.choice(['left', 'right'])
        if spawn_side == 'left':
            x = random.randint(-200, -100)
        else:
            x = random.randint(1300, 1400)

        y = 150
        self.goblins.append(Goblin(x, y))

    def update(self, player):
        now = get_time()
        self.spawn_timer += (now - self.last_spawn_time)
        self.last_spawn_time = now

        if self.spawn_timer > 3.0:
            self.spawn_goblin()
            self.spawn_timer = 0.0

        for goblin in self.goblins:
            goblin.update(player)

        self.goblins = [g for g in self.goblins if g.hp > 0]

    def draw(self, camera_y):
        self.image.draw_to_origin(0, 0, 1200, 800)
        for goblin in self.goblins:
            goblin.draw(camera_y)