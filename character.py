from pico2d import *
from state_machine import StateMachine
from axe import *


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def land_event(e):
    return e[0] == 'LAND'


def land_to_run(e):
    return e[0] == 'LAND_RUN'


def land_to_idle(e):
    return e[0] == 'LAND_IDLE'


def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a


def s_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s


# --- [추가] 낙하 이벤트 ---
def fall(e):
    return e[0] == 'FALL'


# --- ---

class Picking:
    # ... (Picking 클래스 원본과 동일 - 수정 없음) ...
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.axe()

    def do(self):
        character_feet_y = self.character.y - 50
        if self.character.y > self.character.ground_y+5:
            if not self.character.is_jumping:
                self.character.is_jumping = True
                self.character.jump_velocity = 0  # 낙하 시작

            self.character.y += self.character.jump_velocity
            self.character.jump_velocity -= 1  # 중력
            character_feet_y = self.character.y - 50

            if self.character.y <= self.character.ground_y:
                self.character.y = self.character.ground_y + 50
                self.character.is_jumping = False
                self.character.jump_velocity = 0
        # --- ---

    def exit(self, e):
        pass

    def draw(self):
        if self.character.face_dir == 1:
            self.character.pick_image.clip_draw(
                self.character.frame * 33, 0, 33, 36,
                self.character.x, self.character.y, 82, 90
            )
        else:
            self.character.pick_image.clip_composite_draw(
                self.character.frame * 33, 0, 33, 36,
                0, 'h',
                self.character.x, self.character.y, 82, 90
            )


class JUMP:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        # --- [수정] 점프와 낙하 구분 ---
        if space_down(e):  # '점프'
            if not self.character.is_jumping:  # 땅에 있을 때만 점프 가능
                self.character.jump_velocity = 15
                self.character.is_jumping = True
        elif fall(e):  # '낙하'
            if not self.character.is_jumping:  # IDLE/RUN에서 떨어짐
                self.character.jump_velocity = 0  # 속도 없이 중력만 받음
            self.character.is_jumping = True
        # --- ---

        # 점프 중 방향키 입력 처리
        if right_down(e):
            self.character.dir = self.character.face_dir = 1
        elif left_down(e):
            self.character.dir = self.character.face_dir = -1
        # ← space_down 이나 fall(e)일 때는 기존 dir 유지

    def do(self):
        # 좌우 이동 (점프 중에도 가능)
        self.character.x += self.character.dir * 10

        # 점프 물리 (중력 적용)
        self.character.y += self.character.jump_velocity
        self.character.jump_velocity -= 1  # 중력

        # --- [수정] 착지 체크 (ground_y 사용) ---
        if self.character.y <= self.character.ground_y:
            self.character.y = self.character.ground_y
            self.character.is_jumping = False

            # 방향키 상태에 따라 다른 이벤트 발생
            if self.character.key_right_pressed or self.character.key_left_pressed:
                self.character.state_machine.handle_state_event(('LAND_RUN', None))
            else:
                self.character.state_machine.handle_state_event(('LAND_IDLE', None))
        # --- ---

    def exit(self, e):
        self.character.jump_velocity = 0

        if land_to_run(e):
            # 착지 후 RUN 상태로 - dir은 이미 설정되어 있음
            pass
        elif land_to_idle(e):
            self.character.dir = 0

    def draw(self):
        # ... (draw 함수 원본과 동일) ...
        if self.character.face_dir == 1:
            self.character.image.clip_draw(
                self.character.frame * 60, 0, 60, 60,
                self.character.x, self.character.y, 150, 150
            )
        else:
            self.character.image.clip_composite_draw(
                self.character.frame * 60, 0, 60, 60,
                0, 'h',
                self.character.x, self.character.y, 150, 150
            )


class Run:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        if right_down(e):
            self.character.dir = self.character.face_dir = 1
        elif left_down(e):
            self.character.dir = self.character.face_dir = -1
        # up 이벤트는 제거 (IDLE로 전환될 때만 사용)

    def do(self):
        # frame 증가는 Main_Character.update()에서 제어함
        self.character.x += self.character.dir * 10

        if (self.character.y - 50) > self.character.ground_y + 5:
            self.character.state_machine.handle_state_event(('FALL', None))


    def exit(self, e):
        pass

    def draw(self):
        # ... (draw 함수 원본과 동일) ...
        if self.character.face_dir == 1:
            self.character.image.clip_draw(
                self.character.frame * 60, 0, 60, 60,
                self.character.x, self.character.y, 150, 150
            )
        else:
            # 좌우 반전하여 그리기 ('h'는 수평 반전)
            self.character.image.clip_composite_draw(
                self.character.frame * 60, 0, 60, 60,
                0, 'h',
                self.character.x, self.character.y, 150, 150
            )


class Idle:

    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.dir = 0

    def exit(self, e):
        pass

    def do(self):
        # frame 증가는 Main_Character.update()에서 제어함

        # --- [추가] 중력 체크 ---
        if (self.character.y - 50) > self.character.ground_y + 5:
            self.character.state_machine.handle_state_event(('FALL', None))

        pass

    def draw(self):
        # ... (draw 함수 원본과 동일) ...
        if self.character.face_dir == 1:
            self.character.image.clip_draw(
                self.character.frame * 60, 0, 60, 60,
                self.character.x, self.character.y, 150, 150
            )
        else:
            # 좌우 반전하여 그리기 ('h'는 수평 반전)
            self.character.image.clip_composite_draw(
                self.character.frame * 60, 0, 60, 60,
                0, 'h',
                self.character.x, self.character.y, 150, 150
            )


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
        self.axes = []  # 도끼 리스트 추가
        self.thrown_axes = []  # 던지는 도끼 리스트

        # --- [추가] 현재 밟고 있는 땅의 높이 ---
        self.ground_y = 150
        # --- ---

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = JUMP(self)
        self.PICKING = Picking(self)

        self.image = load_image('10001_T1.png')
        self.pick_image = load_image('10001_T1_Picking.png')  # ← 추가!

        # 애니메이션 속도 제어용
        self.last_time = get_time()
        self.anim_acc = 0.0
        self.anim_delay = 0.15
        self.frame_count = 3

        # --- [수정] 상태 머신에 fall 이벤트 추가 ---
        self.state_machine = StateMachine(
            self.IDLE, {
                self.IDLE: {
                    right_down: self.RUN, left_down: self.RUN,
                    space_down: self.JUMP,
                    a_down: self.PICKING,
                    s_down: self.IDLE,  # 던지기 후에도 IDLE 유지
                    fall: self.JUMP  # [추가]
                },
                self.RUN: {
                    right_up: self.IDLE, left_up: self.IDLE,
                    space_down: self.JUMP,
                    a_down: self.PICKING,
                    s_down: self.RUN,  # 던지기 후에도 RUN 유지
                    fall: self.JUMP  # [추가]
                },
                self.JUMP: {
                    right_down: self.JUMP, left_down: self.JUMP,
                    land_to_run: self.RUN,
                    land_to_idle: self.IDLE
                },
                self.PICKING: {
                    a_up: None
                }
            }
        )
        # --- ---

    def update(self):
        # 시간 누적 계산
        now = get_time()
        dt = now - self.last_time
        self.last_time = now

        # 상태(움직임) 업데이트
        self.state_machine.update()

        # 애니메이션 타이머 업데이트 (프레임 속도 제어)
        self.anim_acc += dt
        if self.anim_acc >= self.anim_delay:
            steps = int(self.anim_acc // self.anim_delay)
            self.anim_acc -= steps * self.anim_delay
            self.frame = (self.frame + steps) % self.frame_count

        # 도끼들 업데이트
        self.axes = [axe for axe in self.axes if not axe.update()]
        # 던져진 도끼들 업데이트
        for axe in self.thrown_axes:
            if axe.update():
                self.thrown_axes.remove(axe)

    def draw(self):
        # ... (draw, get_bb, handle_event, axe, throw_axe, clear_projectiles 원본과 동일) ...
        self.state_machine.draw()
        for axe in self.axes:
            axe.draw()
        for axe in self.thrown_axes:
            axe.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50

    def handle_event(self, event):
        # 키 상태 추적
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                self.key_right_pressed = True
            elif event.key == SDLK_LEFT:
                self.key_left_pressed = True
            elif event.key == SDLK_a:
                self.key_a_pressed = True
                if self.state_machine.cur_state in [self.IDLE, self.RUN]:
                    self.prev_state = self.state_machine.cur_state
            elif event.key == SDLK_s:
                # s_down 이벤트가 발생하면, 현재 상태를 유지하면서 throw_axe만 호출
                if self.state_machine.cur_state in [self.IDLE, self.RUN]:
                    self.throw_axe()


        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                self.key_right_pressed = False
            elif event.key == SDLK_LEFT:
                self.key_left_pressed = False
            elif event.key == SDLK_a:
                self.key_a_pressed = False
                # PICKING 상태에서 A키를 뗄 때
                if self.state_machine.cur_state == self.PICKING:
                    # 현재 방향키 상태 확인
                    if self.key_right_pressed:
                        self.dir = self.face_dir = 1
                        self.state_machine.cur_state = self.RUN
                        self.RUN.enter(('INPUT', event))
                    elif self.key_left_pressed:
                        self.dir = self.face_dir = -1
                        self.state_machine.cur_state = self.RUN
                        self.RUN.enter(('INPUT', event))
                    else:
                        # 방향키가 눌리지 않음 → IDLE
                        self.dir = 0
                        self.state_machine.cur_state = self.IDLE
                        self.IDLE.enter(('INPUT', event))
                    return

        self.state_machine.handle_state_event(('INPUT', event))

    def axe(self):
        # Axe 생성 시 x, y, direction 대신 parent=self를 전달합니다.
        # 이제 Axe가 스스로 캐릭터의 위치와 방향을 따라 움직입니다.
        new_axe = Axe(parent=self)
        self.axes.append(new_axe)

    def throw_axe(self):
        # 캐릭터의 손 위치에서 ThrownAxe 생성
        axe_y_pos = self.y + 10
        new_thrown_axe = ThrownAxe(self.x, axe_y_pos, self.face_dir)
        self.thrown_axes.append(new_thrown_axe)

    def clear_projectiles(self):
        self.thrown_axes.clear()
        self.axes.clear()