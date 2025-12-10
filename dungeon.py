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
        self.frame_count = 4
        self.speed = 120

    def enter(self, e):
        self.frame = 0
        self.action_time = 0.0

    def do(self, player):
        dx = player.x - self.goblin.x
        if abs(dx) > 10:
            self.goblin.face_dir = 1 if dx > 0 else -1
            self.goblin.x += self.goblin.face_dir * self.speed * self.goblin.dt

        self.action_time += self.goblin.dt
        self.frame = int(self.action_time * 10) % self.frame_count

        distance = math.sqrt((player.x - self.goblin.x) ** 2 + (player.y - self.goblin.y) ** 2)
        if distance < self.goblin.ATTACK_RANGE:
            self.goblin.state_machine.handle_state_event(('NEAR_PLAYER', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        draw_y = self.goblin.y - camera_y
        frame_width = self.goblin.run_img_w // self.frame_count
        frame_height = self.goblin.run_img_h
        draw_w = frame_width * self.goblin.SCALE
        draw_h = frame_height * self.goblin.SCALE

        if self.goblin.face_dir == -1:
            self.goblin.image_run.clip_draw(self.frame * frame_width, 0, frame_width, frame_height, self.goblin.x,
                                            draw_y, draw_w, draw_h)
        else:
            self.goblin.image_run.clip_composite_draw(self.frame * frame_width, 0, frame_width, frame_height, 0, 'h',
                                                      self.goblin.x, draw_y, draw_w, draw_h)


# --- 고블린 상태 클래스: 공격 (Attack) ---
class GoblinAttack:
    def __init__(self, goblin):
        self.goblin = goblin
        self.frame = 0
        self.action_time = 0.0
        self.frame_count = 6

    def enter(self, e):
        self.frame = 0
        self.action_time = 0.0

    def do(self, player):
        self.action_time += self.goblin.dt
        self.frame = int(self.action_time * 10)

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

        if self.goblin.face_dir == -1:
            self.goblin.image_attack.clip_draw(self.frame * frame_width, 0, frame_width, frame_height, self.goblin.x,
                                               draw_y, draw_w, draw_h)
        else:
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

    ATTACK_RANGE = 80
    SCALE = 3.0

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp = 40
        self.face_dir = -1

        self.last_time = get_time()
        self.dt = 0.0

        # [추가] 넉백 관련 변수
        self.knockback_timer = 0.0
        self.hit_face_dir = 0  # 맞았을 때 날아갈 방향

        if Goblin.image_run is None:
            Goblin.image_run = load_image('60021_1.png')
            Goblin.run_img_w = Goblin.image_run.w
            Goblin.run_img_h = Goblin.image_run.h

        if Goblin.image_attack is None:
            Goblin.image_attack = load_image('60021_1_attack.png')
            Goblin.attack_img_w = Goblin.image_attack.w
            Goblin.attack_img_h = Goblin.image_attack.h

        self.run_state = GoblinRun(self)
        self.attack_state = GoblinAttack(self)

        self.state_machine = StateMachine(self.run_state, {
            self.run_state: {near_player: self.attack_state},
            self.attack_state: {animation_end: self.run_state}
        })

    def update(self, player):
        now = get_time()
        self.dt = now - self.last_time
        self.last_time = now

        # [수정] 넉백 중일 때는 상태 머신(추적/공격)을 멈추고 뒤로 밀려남
        if self.knockback_timer > 0:
            self.knockback_timer -= self.dt
            # 맞은 방향(hit_face_dir)으로 200의 속도로 밀려남
            self.x += self.hit_face_dir * 200 * self.dt

            # 화면 밖으로 나가지 않게 (선택사항)
            self.x = max(0, min(1200, self.x))
        else:
            # 넉백이 끝나면 정상 행동
            self.state_machine.cur_state.do(player)

    def draw(self, camera_y):
        self.state_machine.draw(camera_y)

    def get_bb(self):
        return self.x - 30, self.y - 40, self.x + 30, self.y + 40

    # [수정] hit 함수가 데미지와 함께 '공격 방향'도 받도록 수정
    def hit(self, damage, hit_dir):
        self.hp -= damage
        if self.hp > 0:
            # 살아있다면 넉백 적용
            self.knockback_timer = 0.2  # 0.2초 동안 밀려남
            self.hit_face_dir = hit_dir  # 공격이 날아온 방향대로 밀려남
            return False  # 생존
        else:
            return True  # 사망


# --- Dungeon 클래스 ---
class Dungeon:
    def __init__(self):
        self.image = load_image('bg3_boss.png')
        self.goblins = []

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