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
        self.character.frame = (self.character.frame + 1) % 3
        self.character.x += self.character.dir * 10

    def exit(self, e):
        pass

    def draw(self):
        if self.character.face_dir == 1:
            self.character.image.clip_draw(
                self.character.frame * 60, 0, 60, 60,
                self.character.x, self.character.y
            )
        else:
            # 좌우 반전하여 그리기 ('h'는 수평 반전)
            self.character.image.clip_composite_draw(
                self.character.frame * 60, 0, 60, 60,
                0, 'h',
                self.character.x, self.character.y, 60, 60
            )
class Idle:

    def __init__(self,character):
        self.character = character

    def enter(self,e):
        self.character.dir = 0

    def exit(self,e):
        pass

    def do(self):
        self.character.frame = (self.character.frame + 1) % 3

    def draw(self):
        if self.character.face_dir == 1:
            self.character.image.clip_draw(
                self.character.frame * 60, 0, 60, 60,
                self.character.x, self.character.y
            )
        else:
            # 좌우 반전하여 그리기 ('h'는 수평 반전)
            self.character.image.clip_composite_draw(
                self.character.frame * 60, 0, 60, 60,
                0, 'h',
                self.character.x, self.character.y, 60, 60
            )
class Main_Character:
    def __init__(self):
        self.x, self.y = 600, 400
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.image = load_image('10001_T1.png')
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
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()


    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass