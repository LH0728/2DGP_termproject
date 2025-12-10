# [character.py]
from pico2d import *

from inventory import Inventory
from shop import Shop
from state_machine import StateMachine
from axe import *


# --- HP Bar UI 클래스 ---
class HPBar:
    def __init__(self, character):
        self.character = character
        self.fill_image = load_image('hp.png')
        self.x = 50
        self.y = 50
        self.block_spacing = 18
        self.max_blocks = 10

        try:
            self.font = load_font('ENCR10B.TTF', 16)
        except:
            self.font = None

    def draw(self):
        hp_ratio = max(0.0, min(self.character.hp / self.character.max_hp, 1.0))
        num_blocks_to_draw = int(hp_ratio * self.max_blocks)

        for i in range(num_blocks_to_draw):
            block_x = self.x + (i * self.block_spacing)
            block_y = self.y
            self.fill_image.draw(block_x, block_y)

        if self.font:
            hp_text = f"{int(self.character.hp)}/{self.character.max_hp}"
            self.font.draw(self.x, self.y + 25, hp_text, (255, 255, 255))


# --- 키 입력 이벤트 함수들 ---
def right_up(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def right_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def left_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def space_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def land_event(e): return e[0] == 'LAND'


def land_to_run(e): return e[0] == 'LAND_RUN'


def land_to_idle(e): return e[0] == 'LAND_IDLE'


def a_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def a_up(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a


def s_down(e): return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s


def fall(e): return e[0] == 'FALL'


# --- 상태 클래스들 ---
class Picking:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.axe()

    def do(self):
        if self.character.y > self.character.ground_y + 5:
            if not self.character.is_jumping:
                self.character.is_jumping = True
                self.character.jump_velocity = 0
            self.character.y += self.character.jump_velocity
            self.character.jump_velocity -= 1
            if self.character.y <= self.character.ground_y:
                self.character.y = self.character.ground_y + 50
                self.character.is_jumping = False
                self.character.jump_velocity = 0

    def exit(self, e):
        pass

    def draw(self, camera_y):
        draw_y = self.character.y - camera_y
        if self.character.face_dir == 1:
            self.character.pick_image.clip_draw(self.character.frame * 33, 0, 33, 36, self.character.x, draw_y, 82, 90)
        else:
            self.character.pick_image.clip_composite_draw(self.character.frame * 33, 0, 33, 36, 0, 'h',
                                                          self.character.x, draw_y, 82, 90)


class JUMP:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        if space_down(e):
            if not self.character.is_jumping:
                self.character.jump_velocity = 15
                self.character.is_jumping = True

                # [추가] 점프 사운드 재생
                self.character.jump_sound.play()

        elif fall(e):
            if not self.character.is_jumping: self.character.jump_velocity = 0
            self.character.is_jumping = True

        if right_down(e):
            self.character.dir = self.character.face_dir = 1
        elif left_down(e):
            self.character.dir = self.character.face_dir = -1

    def do(self):
        self.character.x += self.character.dir * 10
        self.character.y += self.character.jump_velocity
        self.character.jump_velocity -= 1
        if self.character.y <= self.character.ground_y:
            self.character.y = self.character.ground_y
            self.character.is_jumping = False
            if self.character.key_right_pressed or self.character.key_left_pressed:
                self.character.state_machine.handle_state_event(('LAND_RUN', None))
            else:
                self.character.state_machine.handle_state_event(('LAND_IDLE', None))

    def exit(self, e):
        self.character.jump_velocity = 0
        if land_to_run(e):
            pass
        elif land_to_idle(e):
            self.character.dir = 0

    def draw(self, camera_y):
        draw_y = self.character.y - camera_y
        if self.character.face_dir == 1:
            self.character.image.clip_draw(self.character.frame * 60, 0, 60, 60, self.character.x, draw_y, 150, 150)
        else:
            self.character.image.clip_composite_draw(self.character.frame * 60, 0, 60, 60, 0, 'h', self.character.x,
                                                     draw_y, 150, 150)


class Run:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        if right_down(e):
            self.character.dir = self.character.face_dir = 1
        elif left_down(e):
            self.character.dir = self.character.face_dir = -1

    def do(self):
        self.character.x += self.character.dir * 5
        if (self.character.y - 50) > self.character.ground_y + 5: self.character.state_machine.handle_state_event(
            ('FALL', None))

    def exit(self, e):
        pass

    def draw(self, camera_y):
        draw_y = self.character.y - camera_y
        if self.character.face_dir == 1:
            self.character.image.clip_draw(self.character.frame * 60, 0, 60, 60, self.character.x, draw_y, 150, 150)
        else:
            self.character.image.clip_composite_draw(self.character.frame * 60, 0, 60, 60, 0, 'h', self.character.x,
                                                     draw_y, 150, 150)


class Idle:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.dir = 0

    def exit(self, e):
        pass

    def do(self):
        if (self.character.y - 50) > self.character.ground_y + 5: self.character.state_machine.handle_state_event(
            ('FALL', None))

    def draw(self, camera_y):
        draw_y = self.character.y - camera_y
        if self.character.face_dir == 1:
            self.character.image.clip_draw(self.character.frame * 60, 0, 60, 60, self.character.x, draw_y, 150, 150)
        else:
            self.character.image.clip_composite_draw(self.character.frame * 60, 0, 60, 60, 0, 'h', self.character.x,
                                                     draw_y, 150, 150)


# --- Main_Character 클래스 ---
class Main_Character:
    def __init__(self):
        self.x, self.y = 600, 150
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.jump_velocity = 0
        self.is_jumping = False
        self.key_right_pressed = False
        self.key_left_pressed = False
        self.key_a_pressed = False
        self.key_s_pressed = False
        self.prev_state = None
        self.axes = []
        self.thrown_axes = []
        self.inventory = Inventory()
        self.shop = Shop()
        self.ground_y = 150

        self.damage = 1

        self.tier_damages = {
            0: 1,
            3: 2,
            1: 6,
            2: 10
        }

        # --- HP 관련 속성 ---
        self.max_hp = 100
        self.hp = 100
        self.hp_bar = HPBar(self)

        self.last_hit_time = 0.0
        self.invincible_duration = 1.0
        self.last_regen_time = get_time()

        self.goblin_kill_count = 0
        self.boss_kill_count = 0

        self.last_throw_time = 0.0
        self.throw_cooldown = 0.5

        # [추가] 점프 효과음 로드
        self.jump_sound = load_wav('jump.mp3')
        self.jump_sound.set_volume(25)  # 소리 크기 (0~128)

        self.swing_sound = load_wav('swing.mp3')
        self.swing_sound.set_volume(60)  # 볼륨 적절히 조절 (0~128)

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = JUMP(self)
        self.PICKING = Picking(self)

        self.image = load_image('10001_T1.png')
        self.pick_image = load_image('10001_T1_Picking.png')

        self.last_time = get_time()
        self.anim_acc = 0.0
        self.anim_delay = 0.15
        self.frame_count = 3

        self.state_machine = StateMachine(
            self.IDLE, {
                self.IDLE: {right_down: self.RUN, left_down: self.RUN, space_down: self.JUMP, a_down: self.PICKING,
                            s_down: self.IDLE, fall: self.JUMP},
                self.RUN: {right_up: self.IDLE, left_up: self.IDLE, space_down: self.JUMP, a_down: self.PICKING,
                           s_down: self.RUN, fall: self.JUMP},
                self.JUMP: {right_down: self.JUMP, left_down: self.JUMP, land_to_run: self.RUN,
                            land_to_idle: self.IDLE},
                self.PICKING: {a_up: None}
            }
        )

    def update(self):
        now = get_time()
        dt = now - self.last_time
        self.last_time = now
        self.state_machine.update()
        self.anim_acc += dt
        if self.anim_acc >= self.anim_delay:
            steps = int(self.anim_acc // self.anim_delay)
            self.anim_acc -= steps * self.anim_delay
            self.frame = (self.frame + steps) % self.frame_count
        self.axes = [axe for axe in self.axes if not axe.update()]
        for axe in self.thrown_axes:
            if axe.update():
                self.thrown_axes.remove(axe)

    def draw(self, camera_y):
        self.state_machine.draw(camera_y)
        for axe in self.axes:
            axe.draw(camera_y)
        for axe in self.thrown_axes:
            axe.draw(camera_y)

        self.hp_bar.draw()

    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50

    def hit(self, damage):
        if get_time() - self.last_hit_time > self.invincible_duration:
            self.hp = max(0, self.hp - damage)
            self.last_hit_time = get_time()
            print(f"[Player Hit] HP: {self.hp}")
            return True
        return False

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                self.key_right_pressed = True
            elif event.key == SDLK_LEFT:
                self.key_left_pressed = True
            elif event.key == SDLK_a:
                self.key_a_pressed = True
                if self.state_machine.cur_state in [self.IDLE, self.RUN]: self.prev_state = self.state_machine.cur_state
            elif event.key == SDLK_s:
                if self.state_machine.cur_state in [self.IDLE, self.RUN]: self.throw_axe()

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                self.key_right_pressed = False
            elif event.key == SDLK_LEFT:
                self.key_left_pressed = False
            elif event.key == SDLK_a:
                self.key_a_pressed = False
                if self.state_machine.cur_state == self.PICKING:
                    if self.key_right_pressed:
                        self.dir = self.face_dir = 1
                        self.state_machine.cur_state = self.RUN
                        self.RUN.enter(('INPUT', event))
                    elif self.key_left_pressed:
                        self.dir = self.face_dir = -1
                        self.state_machine.cur_state = self.RUN
                        self.RUN.enter(('INPUT', event))
                    else:
                        self.dir = 0
                        self.state_machine.cur_state = self.IDLE
                        self.IDLE.enter(('INPUT', event))
                    return

        self.state_machine.handle_state_event(('INPUT', event))

    def axe(self):
        self.swing_sound.play()
        new_axe = Axe(parent=self)
        self.axes.append(new_axe)

    def throw_axe(self):
        if get_time() - self.last_throw_time < self.throw_cooldown:
            return

        self.last_throw_time = get_time()

        self.swing_sound.play()

        axe_y_pos = self.y + 10
        new_thrown_axe = ThrownAxe(self.x, axe_y_pos, self.face_dir)
        self.thrown_axes.append(new_thrown_axe)
        print("도끼 투척!")

    def clear_projectiles(self):
        self.thrown_axes.clear()
        self.axes.clear()

    def equip_pickaxe(self, tier):
        self.inventory.pickaxe_tier = tier
        Axe.set_tier(tier)
        ThrownAxe.set_tier(tier)
        self.damage = self.tier_damages.get(tier, 1)
        print(f"[Character] 곡괭이 교체: Tier {tier}, 공격력: {self.damage}")