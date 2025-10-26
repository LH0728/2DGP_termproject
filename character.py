from pico2d import *
from state_machine import StateMachine

def right_up(e):
    return e[0] == 'INPUT'and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def right_down(e):
    return e[0] == 'INPUT'and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def left_down(e):
    return e[0] == 'INPUT'and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):
    return e[0] == 'INPUT'and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT
def space_down(e):
    return e[0] == 'INPUT'and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


class JUMP:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        pass

    def do(self):
        pass

    def exit(self, e):
        pass

    def draw(self):
        pass

class Run:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.dir = 1
        if right_down(e) or left_up(e):
            self.character.dir = self.character.face_dir = 1
        elif left_down(e) or right_up(e):
            self.character.dir = self.character.face_dir = -1
        # 그 외의 경우는 현재 face_dir 유지

    def do(self):
        # frame 증가는 Main_Character.update()에서 제어함
        self.character.x += self.character.dir * 10

    def exit(self, e):
        pass

    def draw(self):
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

    def __init__(self,character):
        self.character = character

    def enter(self,e):
        self.character.dir = 0

    def exit(self,e):
        pass

    def do(self):
        # frame 증가는 Main_Character.update()에서 제어함
        pass

    def draw(self):
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
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.image = load_image('10001_T1.png')

        # 애니메이션 속도 제어용
        self.last_time = get_time()
        self.anim_acc = 0.0
        self.anim_delay = 0.15  # 초 단위, 프레임 하나 당 0.15초 -> 느리게
        self.frame_count = 3

        self.state_machine = StateMachine(
            self.IDLE, {
                self.IDLE: {
                    right_up: self.RUN, left_up: self.RUN, right_down: self.RUN, left_down: self.RUN
                },
                self.RUN: {
                    right_down: self.IDLE, left_down: self.IDLE, right_up: self.IDLE, left_up: self.IDLE    # 왼쪽 키 떼면 정지
                }
            }
        )
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

    def draw(self):
        self.state_machine.draw()


    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass