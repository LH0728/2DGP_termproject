from pico2d import *
import math
import random
from state_machine import StateMachine


# -----------------------------------------------------------
# [보스 팔(Arm) 클래스]
# -----------------------------------------------------------
class YormungandArm:
    image = None

    def __init__(self, x):
        self.x = x
        self.y = -200  # 땅 밑 시작
        self.target_y = 130
        self.rise_speed = 400

        if YormungandArm.image is None:
            self.image = load_image('Yormungand_Arm.png')

        self.frame_count = 6
        self.width = self.image.w // self.frame_count
        self.height = self.image.h

        self.frame = 0
        self.timer = 0
        self.scale = 7.0

    def update(self, dt):
        if self.y < self.target_y:
            self.y += self.rise_speed * dt
        else:
            self.y = self.target_y

        self.timer += dt
        self.frame = int(self.timer * 10) % self.frame_count
        return False

    def draw(self, camera_y):
        draw_y = self.y - camera_y
        rotation = math.radians(-90)  # 위를 향함

        draw_w = self.width * self.scale
        draw_h = self.height * self.scale

        self.image.clip_composite_draw(
            self.frame * self.width, 0,
            self.width, self.height,
            rotation, '',
            self.x, draw_y, draw_w, draw_h
        )

    def get_bb(self):
        # [수정] 피격 범위 축소
        # 나누는 값을 키워서 박스를 더 작게 만듦
        # 기존: // 3, // 2 -> 수정: // 4, // 2.5
        hit_w = (self.height * self.scale) // 4
        hit_h = (self.width * self.scale) // 2.5

        return self.x - hit_w, self.y - hit_h, self.x + hit_w, self.y + hit_h


# -----------------------------------------------------------
# [보스 상태 클래스들]
# -----------------------------------------------------------

# 1. [등장]
class BossEntrance:
    def __init__(self, boss):
        self.boss = boss
        self.speed = 200

    def enter(self, e):
        print("Boss Entering...")
        self.boss.face_dir = -1
        self.boss.x = 1800
        self.boss.phase_timer = 0.0

    def do(self, player):
        target_x = 1000
        if self.boss.x > target_x:
            self.boss.x -= self.speed * self.boss.dt
        else:
            self.boss.x = target_x
            self.boss.state_machine.handle_state_event(('ARRIVED', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        self.boss.draw_body(camera_y)


# 2. [대기]
class BossIdle:
    def __init__(self, boss):
        self.boss = boss
        self.action_time = 0.0

    def enter(self, e):
        self.action_time = 0.0
        self.boss.frame = 0
        # 재진입 시 타이머 초기화하지 않음 (페이즈 유지)

    def do(self, player):
        self.boss.phase_timer += self.boss.dt
        self.action_time += self.boss.dt

        time_per_action = 1.0
        frames_per_action = self.boss.frame_count
        self.boss.frame = int(self.action_time * frames_per_action / time_per_action) % frames_per_action

        if self.boss.phase_timer > 7.0:
            self.boss.state_machine.handle_state_event(('PHASE_TIMEOUT', None))
            return

        if self.action_time > 3.0:
            self.boss.state_machine.handle_state_event(('ATTACK_START', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        self.boss.draw_body(camera_y)


# 3. [공격]
class BossAttack:
    def __init__(self, boss):
        self.boss = boss
        self.action_time = 0.0
        self.anim_duration = 1.0

    def enter(self, e):
        self.action_time = 0.0
        self.boss.frame = 0
        print("Boss Attack!")

    def do(self, player):
        self.boss.phase_timer += self.boss.dt
        self.action_time += self.boss.dt
        total_frames = self.boss.attack_frame_count

        if self.action_time >= self.anim_duration:
            self.boss.frame = total_frames - 1
            if self.boss.phase_timer > 7.0:
                self.boss.state_machine.handle_state_event(('PHASE_TIMEOUT', None))
            else:
                self.boss.state_machine.handle_state_event(('ANIMATION_END', None))
        else:
            self.boss.frame = int((self.action_time / self.anim_duration) * total_frames)

    def exit(self, e):
        pass

    def draw(self, camera_y):
        draw_y = self.boss.y - camera_y
        width = self.boss.attack_frame_width * self.boss.scale
        height = self.boss.attack_frame_height * self.boss.scale

        self.boss.image_attack.clip_draw(
            self.boss.frame * self.boss.attack_frame_width, 0,
            self.boss.attack_frame_width, self.boss.attack_frame_height,
            self.boss.x, draw_y, width, height
        )


# 4. [퇴장] (페이즈 전환용)
class BossExit:
    def __init__(self, boss):
        self.boss = boss
        self.speed = 200

    def enter(self, e):
        print("Boss Exiting (Phase Change)...")

    def do(self, player):
        target_x = 1800
        self.boss.x += self.speed * self.boss.dt
        self.boss.frame = (self.boss.frame + 1) % self.boss.frame_count

        if self.boss.x >= target_x:
            self.boss.x = target_x
            self.boss.state_machine.handle_state_event(('HIDDEN', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        self.boss.draw_body(camera_y)


# 5. [팔 공격]
class BossArmPhase:
    def __init__(self, boss):
        self.boss = boss
        self.spawn_timer = 0.0
        self.spawn_count = 0

    def enter(self, e):
        print("Arm Phase Start!")
        self.boss.phase_timer = 0.0
        self.spawn_timer = 0.0
        self.spawn_count = 0
        self.boss.arms.clear()

    def do(self, player):
        self.boss.phase_timer += self.boss.dt
        self.spawn_timer += self.boss.dt

        if self.spawn_count < 2 and self.spawn_timer > 2.0:
            self.spawn_timer = 0.0
            self.spawn_count += 1
            new_arm = YormungandArm(player.x)
            self.boss.arms.append(new_arm)
            print(f"Arm Spawned! ({self.spawn_count}/2)")

        if self.boss.phase_timer > 7.0:
            self.boss.arms.clear()
            self.boss.state_machine.handle_state_event(('PHASE_TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        pass

    # 6. [추가] [사망] 오른쪽으로 완전히 퇴장 (죽었을 때)


class BossDeath:
    def __init__(self, boss):
        self.boss = boss
        self.speed = 100  # 천천히 퇴장

    def enter(self, e):
        print("Boss Died... Sliding Out.")
        # 팔 공격 중 죽었을 수도 있으니 팔 제거
        self.boss.arms.clear()

    def do(self, player):
        # 오른쪽 끝으로 계속 이동
        target_x = 2000  # 화면 밖 아주 멀리
        self.boss.x += self.speed * self.boss.dt

        # Idle 애니메이션 재생하며 슬픈 퇴장
        self.boss.frame = (self.boss.frame + 1) % self.boss.frame_count

    def exit(self, e):
        pass

    def draw(self, camera_y):
        self.boss.draw_body(camera_y)


# -----------------------------------------------------------
# [보스 메인 클래스]
# -----------------------------------------------------------
def arrived(e): return e[0] == 'ARRIVED'


def attack_start(e): return e[0] == 'ATTACK_START'


def anim_end(e): return e[0] == 'ANIMATION_END'


def phase_timeout(e): return e[0] == 'PHASE_TIMEOUT'


def hidden(e): return e[0] == 'HIDDEN'


def dead(e): return e[0] == 'DEAD'  # 사망 이벤트


class Yormungand:
    image = None
    image_attack = None

    def __init__(self, x, y):
        self.x = 1800
        self.y = y
        self.hp = 500
        self.max_hp = 500
        self.face_dir = -1
        self.damage = 20

        if Yormungand.image is None:
            self.image = load_image('Yormungand_Idle.png')
        self.frame_width = 89
        self.frame_height = 45
        self.frame_count = 6

        if Yormungand.image_attack is None:
            self.image_attack = load_image('Yormungand_Attack.png')
        self.attack_frame_width = 101
        self.attack_frame_height = 54
        self.attack_frame_count = 8

        self.scale = 7.0
        self.dt = 0.0
        self.last_time = get_time()
        self.frame = 0

        self.phase_timer = 0.0
        self.arms = []

        self.state_entrance = BossEntrance(self)
        self.state_idle = BossIdle(self)
        self.state_attack = BossAttack(self)
        self.state_exit = BossExit(self)
        self.state_arm = BossArmPhase(self)
        self.state_death = BossDeath(self)  # 사망 상태 추가

        self.state_machine = StateMachine(self.state_entrance, {
            self.state_entrance: {arrived: self.state_idle, dead: self.state_death},
            self.state_idle: {attack_start: self.state_attack, phase_timeout: self.state_exit, dead: self.state_death},
            self.state_attack: {anim_end: self.state_idle, phase_timeout: self.state_exit, dead: self.state_death},
            self.state_exit: {hidden: self.state_arm, dead: self.state_death},
            self.state_arm: {phase_timeout: self.state_entrance, dead: self.state_death},
            self.state_death: {}  # 사망 상태에서는 전이 없음
        })

    def update(self, player):
        now = get_time()
        self.dt = now - self.last_time
        self.last_time = now

        if self.dt > 0.05:
            self.dt = 0.01

        self.state_machine.cur_state.do(player)
        self.arms = [arm for arm in self.arms if not arm.update(self.dt)]

    def draw(self, camera_y):
        for arm in self.arms:
            arm.draw(camera_y)

        self.state_machine.draw(camera_y)

        # 죽거나 팔 공격 중일 때는 HP바 숨김
        if self.state_machine.cur_state != self.state_arm and self.state_machine.cur_state != self.state_death:
            self.draw_hp_bar(camera_y)

    def draw_body(self, camera_y):
        draw_y = self.y - camera_y
        width = self.frame_width * self.scale
        height = self.frame_height * self.scale

        self.image.clip_draw(
            self.frame * self.frame_width, 0,
            self.frame_width, self.frame_height,
            self.x, draw_y, width, height
        )

    def draw_hp_bar(self, camera_y):
        draw_y = self.y - camera_y + 150
        draw_rectangle(self.x - 150, draw_y - 15, self.x + 150, draw_y + 15)
        hp_ratio = max(0, self.hp / self.max_hp)
        current_bar_width = 300 * hp_ratio
        for i in range(int(current_bar_width)):
            draw_line(self.x - 150 + i, draw_y - 14, self.x - 150 + i, draw_y + 14)

    def get_bb(self):
        # 팔 공격, 퇴장, 사망 상태일 때는 충돌 박스 치워버림
        if self.state_machine.cur_state in [self.state_arm, self.state_exit, self.state_death]:
            return -1000, -1000, -900, -900

        height = (self.frame_height * self.scale) // 2

        if self.state_machine.cur_state == self.state_attack:
            width = (self.attack_frame_width * self.scale) // 2
            # [수정] 공격 피격 범위 축소 (살짝 줄임)
            # -200 -> -150으로 줄이고, 위아래 여백(+20)을 둠
            return self.x - width - 150, self.y - height + 20, self.x + width - 40, self.y + height - 20
        else:
            width = (self.frame_width * self.scale) // 2
            return self.x - width + 40, self.y - height, self.x + width - 40, self.y + height

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            # [중요] 죽으면 바로 상태 변경 이벤트 발생
            self.state_machine.handle_state_event(('DEAD', None))
            return True  # 죽었음을 알림
        return False