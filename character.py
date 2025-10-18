from pico2d import *

def right_up(e):
    pass

def right_down(e):
    pass

def left_up(e):
    pass

def left_down(e):
    pass

def Run(self):
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.dir = 1
        if right_down(e) or left_up(e):
            self.character.dir = self.character.face_dir = 1
        elif left_down(e) or right_up(e):
            self.character.dir = self.character.face_dir = -1
    pass


class Main_Character:
    def __init__(self):
        self.x, self.y = 600, 400
        self.frame = 0
        self.face_dir = 1
        self.RUN = Run(self)
        self.image = load_image('10001_T1.png')
    def update(self):
        self.frame = (self.frame + 1) % 3

    def draw(self):
        self.image.clip_draw(self.frame * 60, 0, 60, 60, self.x, self.y)


    def handle_evnet(self, event):
        pass