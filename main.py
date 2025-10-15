from pico2d import *

def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


class Main_Character:
    def __init__(self):
        self.x, self.y = 600, 400
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('10001_T1.png')
    def update(self):
        self.frame = (self.frame + 1) % 3

    def draw(self):
        self.image.clip_draw(self.frame * 60, 0, 60, 60, self.x, self.y)


def reset_world():
    global world
    global main_character

    world = []

    main_character = Main_Character()
    world.append(main_character)

def update_world():
    for o in world:
        o.update()
    pass

def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()

open_canvas(1200, 800)
running = True

reset_world()

while running :
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()