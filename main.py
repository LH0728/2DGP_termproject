from pico2d import *
from character import Main_Character
from village import Village
from mine import Mine

# 월드 상태
village_world = []
mine_world = []
current_world = None

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            # 현재 월드의 캐릭터에게만 이벤트를 전달합니다.
            main_character.handle_event(event)

def setup_worlds():
    global village_world, mine_world, current_world
    global main_character

    # 캐릭터 생성 (한 번만)
    main_character = Main_Character()

    # 마을 월드 설정
    village = Village()
    village_world = [village, main_character]

    # 광산 월드 설정
    mine = Mine()
    mine_world = [mine, main_character]

    # 시작은 마을 월드
    current_world = village_world

def update_world():
    global current_world
    for o in current_world:
        o.update()

    # 월드 전환 로직
    if current_world == village_world and main_character.x > 1200:
        current_world = mine_world
        main_character.x = 10 # 화면 왼쪽에서 나타남
    elif current_world == mine_world and main_character.x < 0:
        current_world = village_world
        main_character.x = 1190 # 화면 오른쪽에서 나타남


def render_world():
    clear_canvas()
    for o in current_world:
        o.draw()
    update_canvas()

open_canvas(1200, 800)
running = True

# reset_world() 대신 setup_worlds() 호출
setup_worlds()

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()