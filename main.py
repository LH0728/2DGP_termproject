# [main.py] - check_collisions 함수 수정 및 전체 코드
from pico2d import *
from character import Main_Character
from village import Village, Merchant
from mine import Mine
from dungeon import Dungeon
from hit import HitEffect
from mine_2 import Mine_2, Mineral
import random

# 월드 상태
village_world = []
mine_world = []
mine_2_world = []
dungeon_world = []
current_world = None
hit_effects = []

camera_y = 0.0

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
    global merchant

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False


        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            click_x, click_y = event.x, 800 - 1 - event.y

            if main_character.shop.visible:
                main_character.shop.handle_event(event, main_character, merchant)

            else:
                if current_world == village_world and merchant:
                    if merchant.x - 50 <= click_x <= merchant.x + 50 and merchant.y - 50 <= click_y <= merchant.y + 50:
                        main_character.shop.toggle()

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                if main_character.shop.visible:
                    main_character.shop.visible = False
                elif main_character.inventory.visible:
                    main_character.inventory.visible = False
                else:  # 게임 종료
                    running = False

            elif event.key == SDLK_e:
                main_character.inventory.toggle()

            elif event.key == SDLK_UP:
                if current_world == mine_world and 500 < main_character.x < 700:
                    change_world(mine_2_world)
                    main_character.x, main_character.y = 600, 230

            elif event.key == SDLK_DOWN:
                if current_world == mine_2_world:
                    change_world(mine_world)
                    main_character.x, main_character.y = 600, 150

            else:
                main_character.handle_event(event)

        elif event.type == SDL_KEYUP:
            main_character.handle_event(event)

def setup_worlds():
    global village_world, mine_world, mine_2_world, dungeon_world, current_world
    global main_character, hit_effects, merchant

    global camera_y
    camera_y = 0.0
    # 캐릭터 생성 (한 번만)
    main_character = Main_Character()

    # 마을 월드 설정
    village = Village()
    merchant = Merchant(800, 150)
    village_world = [village, merchant, main_character]

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
    global current_world, hit_effects
    global camera_y
    for o in current_world:
        if isinstance(o, (Mine, Mine_2, Mineral, Dungeon)):
            o.update(main_character)
        else:
            o.update()

    # 피격 이펙트 업데이트 및 제거
    hit_effects = [effect for effect in hit_effects if not effect.update()]

    # 월드 전환 로직 (좌우)
    if current_world == village_world and main_character.x > 1200:
        change_world(mine_world)
        main_character.x = 10
        main_character.y = 150
    elif current_world == mine_world and main_character.x < 0:
        change_world(village_world)
        main_character.x = 1190
        main_character.y = 150
    elif current_world == village_world and main_character.x < 0:
        change_world(dungeon_world)
        main_character.x = 1190
        main_character.y = 150
    elif current_world == dungeon_world and main_character.x > 1200:
        change_world(village_world)
        main_character.x = 10
        main_character.y = 150

    if current_world == mine_2_world:
        target_camera_y = main_character.y - 300.0
        camera_y = min(0.0, target_camera_y)
        mine_2_map = mine_2_world[0]
        mine_2_map.procedural_update(camera_y)

def change_world(new_world):
    global current_world
    global camera_y
    camera_y = 0.0
    current_world = new_world
    main_character.clear_projectiles()
    hit_effects.clear()

    if new_world != mine_2_world:
        main_character.ground_y = 150
    if new_world == village_world or new_world == mine_world or new_world == dungeon_world:
        main_character.y = 150
        main_character.is_jumping = False
        main_character.jump_velocity = 0


def check_collisions():
    global current_world, main_character

    # --- 광산 1 충돌 처리 (두더지는 체력이 1이라 데미지 상관없음) ---
    if current_world == mine_world:
        # (기존 코드와 동일)
        mine = mine_world[0]
        moles_to_remove = []
        axes_to_remove = []

        for axe in main_character.axes:
            for mole in mine.moles:
                if mole.hp <= 0: continue
                if collide(axe, mole):
                    if mole.hit(main_character.face_dir):
                        if mole not in moles_to_remove: moles_to_remove.append(mole)
                    hit_effects.append(HitEffect(mole.x, mole.y))

        for thrown_axe in main_character.thrown_axes:
            if thrown_axe in axes_to_remove: continue
            for mole in mine.moles:
                if mole.hp <= 0: continue
                if collide(thrown_axe, mole):
                    if mole.hit(thrown_axe.direction):
                        if mole not in moles_to_remove: moles_to_remove.append(mole)
                    axes_to_remove.append(thrown_axe)
                    hit_effects.append(HitEffect(mole.x, mole.y))
                    break

        for mole in moles_to_remove:
            if mole in mine.moles: mine.moles.remove(mole)
        for thrown_axe in axes_to_remove:
            if thrown_axe in main_character.thrown_axes: main_character.thrown_axes.remove(thrown_axe)

    # --- 광산 2 충돌 처리 (기존 코드와 동일) ---
    elif current_world == mine_2_world:
        mine_2 = mine_2_world[0]
        soils_to_remove = []
        axes_to_remove = []

        for soil in mine_2.soils:
            if collide(main_character, soil):
                left_c, bottom_c, right_c, top_c = main_character.get_bb()
                left_s, bottom_s, right_s, top_s = soil.get_bb()
                overlap_x = min(right_c, right_s) - max(left_c, left_s)
                overlap_y = min(top_c, top_s) - max(bottom_c, bottom_s)

                if overlap_x < overlap_y:
                    if main_character.x < soil.x: main_character.x -= overlap_x
                    else: main_character.x += overlap_x
                else:
                    if main_character.y < soil.y and main_character.jump_velocity > 0:
                        main_character.y -= overlap_y
                        main_character.jump_velocity = 0

        for axe in main_character.axes:
            for soil in mine_2.soils:
                if soil in soils_to_remove: continue
                if collide(axe, soil):
                    if soil.hit(): soils_to_remove.append(soil)
                    hit_effects.append(HitEffect(soil.x, soil.y))

        for thrown_axe in main_character.thrown_axes:
            if thrown_axe in axes_to_remove: continue
            for soil in mine_2.soils:
                if collide(thrown_axe, soil):
                    if soil not in soils_to_remove: soils_to_remove.append(soil)
                    axes_to_remove.append(thrown_axe)
                    hit_effects.append(HitEffect(soil.x, soil.y))
                    break

        for soil in soils_to_remove:
            if soil in mine_2.soils:
                mine_2.soils.remove(soil)
                if random.random() < 0.3:
                    mineral = Mineral(soil.x, soil.y + 20)
                    current_world.append(mineral)
        for thrown_axe in axes_to_remove:
            if thrown_axe in main_character.thrown_axes: main_character.thrown_axes.remove(thrown_axe)

        minerals_to_remove = []
        now = get_time()
        for o in current_world:
            if isinstance(o, Mineral):
                if now - o.spawn_time < 0.5: continue
                if collide(main_character, o):
                    main_character.inventory.add(o.type)
                    minerals_to_remove.append(o)
        for m in minerals_to_remove:
            current_world.remove(m)

    # --- [수정] 던전 충돌 처리 ---
    elif current_world == dungeon_world:
        dungeon = dungeon_world[0]
        goblins_to_remove = []
        axes_to_remove = []

        # 1. 고블린 -> 캐릭터 공격
        for goblin in dungeon.goblins:
            if goblin.hp <= 0: continue
            if collide(main_character, goblin):
                if main_character.hit(10):
                    hit_effects.append(HitEffect(main_character.x, main_character.y))

        # 2. 캐릭터 -> 고블린 공격 (근접 도끼)
        for axe in main_character.axes:
            for goblin in dungeon.goblins:
                if goblin.hp <= 0: continue
                if collide(axe, goblin):
                    # [수정] main_character.damage 를 사용하여 데미지 적용
                    if goblin.hit(main_character.damage, main_character.face_dir):
                        if goblin not in goblins_to_remove: goblins_to_remove.append(goblin)
                    hit_effects.append(HitEffect(goblin.x, goblin.y))

        # 3. 캐릭터 -> 고블린 공격 (던지는 도끼)
        for thrown_axe in main_character.thrown_axes:
            if thrown_axe in axes_to_remove: continue
            for goblin in dungeon.goblins:
                if goblin.hp <= 0: continue
                if collide(thrown_axe, goblin):
                    # [수정] main_character.damage 를 사용하여 데미지 적용
                    if goblin.hit(main_character.damage, thrown_axe.direction):
                        if goblin not in goblins_to_remove: goblins_to_remove.append(goblin)
                    axes_to_remove.append(thrown_axe)
                    hit_effects.append(HitEffect(goblin.x, goblin.y))
                    break

        # 사망한 고블린 및 사용된 도끼 제거
        for goblin in goblins_to_remove:
            if goblin in dungeon.goblins: dungeon.goblins.remove(goblin)
        for thrown_axe in axes_to_remove:
            if thrown_axe in main_character.thrown_axes: main_character.thrown_axes.remove(thrown_axe)

def render_world():
    global camera_y
    clear_canvas()
    for o in current_world:
        o.draw(camera_y)

    for effect in hit_effects:
        effect.draw(camera_y)

    main_character.inventory.draw()
    main_character.shop.draw(main_character)

    update_canvas()

open_canvas(1200, 800)
running = True

setup_worlds()

while running:
    handle_events()
    update_world()
    check_collisions()
    render_world()
    delay(0.01)

close_canvas()