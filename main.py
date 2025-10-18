from pico2d import *
from character import Main_Character

def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            Main_Character.handle_evnet(event)


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
    delay(0.1)

close_canvas()