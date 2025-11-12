from pico2d import *
from character import Main_Character
from village import Village
from mine import Mine
from dungeon import Dungeon

# 월드 상태
village_world = []
mine_world = []
dungeon_world = []
current_world = None

def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True



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
    global village_world, mine_world, dungeon_world, current_world
    global main_character

    # 캐릭터 생성 (한 번만)
    main_character = Main_Character()

    # 마을 월드 설정
    village = Village()
    village_world = [village, main_character]

    # 광산 월드 설정
    mine = Mine()
    mine_world = [mine, main_character]

    # 던전 월드 설정
    dungeon = Dungeon()
    dungeon_world = [dungeon, main_character]

    # 시작은 마을 월드
    current_world = village_world

def update_world():
    global current_world, village_world, mine_world, dungeon_world
    for o in current_world:
        if isinstance(o, Mine):
            o.update(main_character)
        else:
            o.update()

    # 충돌 처리 (광산 월드에서만)
    if current_world == mine_world:
        mine = mine_world[0]  # Mine 객체 가져오기
        moles_to_remove = []
        axes_to_remove = []

        # 1. 휘두르는 도끼와 두더지 충돌
        for axe in main_character.axes:
            for mole in mine.moles:
                if collide(axe, mole):
                    # mole.hit()을 호출하고, True를 반환하면(죽었으면) 제거 목록에 추가
                    if mole.hit(main_character.face_dir):
                        if mole not in moles_to_remove:
                            moles_to_remove.append(mole)

        # 2. 던지는 도끼와 두더지 충돌
        for thrown_axe in main_character.thrown_axes:
            for mole in mine.moles:
                if collide(thrown_axe, mole):
                    # mole.hit()을 호출하고, True를 반환하면(죽었으면) 제거 목록에 추가
                    if mole.hit(thrown_axe.direction):
                        if mole not in moles_to_remove:
                            moles_to_remove.append(mole)

                    # 던진 도끼는 충돌 시 항상 제거
                    if thrown_axe not in axes_to_remove:
                        axes_to_remove.append(thrown_axe)

        # 충돌된 객체들 제거
        for mole in moles_to_remove:
            if mole in mine.moles:
                mine.moles.remove(mole)
        for thrown_axe in axes_to_remove:
            if thrown_axe in main_character.thrown_axes:
                main_character.thrown_axes.remove(thrown_axe)


    # 월드 전환 로직
    if current_world == village_world and main_character.x > 1200:
        current_world = mine_world
        main_character.x = 10 # 화면 왼쪽에서 나타남
        main_character.clear_projectiles()
    elif current_world == mine_world and main_character.x < 0:
        current_world = village_world
        main_character.x = 1190 # 화면 오른쪽에서 나타남
        main_character.clear_projectiles()
    elif current_world == village_world and main_character.x < 0:
        current_world = dungeon_world
        main_character.x = 1190 # 화면 오른쪽에서 나타남
        main_character.clear_projectiles()
    elif current_world == dungeon_world and main_character.x > 1200:
        current_world = village_world
        main_character.x = 10  # 화면 오른쪽에서 나타남
        main_character.clear_projectiles()


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