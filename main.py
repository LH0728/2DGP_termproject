from pico2d import *
from character import Main_Character
from village import Village
from mine import Mine
from dungeon import Dungeon
from hit import HitEffect
from mine_2 import Mine_2

# 월드 상태
village_world = []
mine_world = []
mine_2_world = []
dungeon_world = []
current_world = None
hit_effects = []


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
        elif event.type == SDL_KEYDOWN and event.key == SDLK_UP:
            # mine에서 mine_2로 이동
            if current_world == mine_world and 500 < main_character.x < 700:
                change_world(mine_2_world)
                main_character.x, main_character.y = 600, 150 # mine_2 시작 위치
        elif event.type == SDL_KEYDOWN and event.key == SDLK_DOWN:
            # mine_2에서 mine으로 이동
            if current_world == mine_2_world:
                change_world(mine_world)
                main_character.x, main_character.y = 600, 150 # mine 시작 위치
        else:
            # 현재 월드의 캐릭터에게만 이벤트를 전달합니다.
            main_character.handle_event(event)

def setup_worlds():
    global village_world, mine_world, mine_2_world, dungeon_world, current_world
    global main_character, hit_effects

    # 캐릭터 생성 (한 번만)
    main_character = Main_Character()

    # 마을 월드 설정
    village = Village()
    village_world = [village, main_character]

    # 광산 월드 설정
    mine = Mine()
    mine_world = [mine, main_character]

    # 광산2 월드 설정
    mine_2 = Mine_2()
    mine_2_world = [mine_2, main_character]

    # 던전 월드 설정
    dungeon = Dungeon()
    dungeon_world = [dungeon, main_character]

    # 시작은 마을 월드
    current_world = village_world
    hit_effects = []

def update_world():
    global current_world, village_world, mine_world, dungeon_world, hit_effects
    for o in current_world:
        if isinstance(o, (Mine, Mine_2)):
            o.update(main_character)
        else:
            o.update()

    # 피격 이펙트 업데이트 및 제거
    hit_effects = [effect for effect in hit_effects if not effect.update()]

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
                    # 피격 이펙트 생성
                    hit_effects.append(HitEffect(mole.x, mole.y))


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

                    # 피격 이펙트 생성
                    hit_effects.append(HitEffect(mole.x, mole.y))


        # 충돌된 객체들 제거
        for mole in moles_to_remove:
            if mole in mine.moles:
                mine.moles.remove(mole)
        for thrown_axe in axes_to_remove:
            if thrown_axe in main_character.thrown_axes:
                main_character.thrown_axes.remove(thrown_axe)


    # 월드 전환 로직 (좌우)
    if current_world == village_world and main_character.x > 1200:
        change_world(mine_world)
        main_character.x = 10 # 화면 왼쪽에서 나타남
    elif current_world == mine_world and main_character.x < 0:
        change_world(village_world)
        main_character.x = 1190 # 화면 오른쪽에서 나타남
    elif current_world == village_world and main_character.x < 0:
        change_world(dungeon_world)
        main_character.x = 1190 # 화면 오른쪽에서 나타남
    elif current_world == dungeon_world and main_character.x > 1200:
        change_world(village_world)
        main_character.x = 10  # 화면 오른쪽에서 나타남

def change_world(new_world):
    """월드를 전환하는 함수"""
    global current_world
    current_world = new_world
    main_character.clear_projectiles()
    hit_effects.clear()


def render_world():
    clear_canvas()
    for o in current_world:
        o.draw()
    # 피격 이펙트 그리기
    for effect in hit_effects:
        effect.draw()
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