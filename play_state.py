from pico2d import *
import game_framework
import game_over_state  # 사망 시 이동할 상태

# 기존 import들
from character import Main_Character
from village import Village, Merchant, QuestNPC
from mine import Mine
from dungeon import Dungeon
from hit import HitEffect
from mine_2 import Mine_2, Mineral
from boss_map import BossStage
import random

# 전역 변수들
village_world = []
mine_world = []
mine_2_world = []
dungeon_world = []
boss_world = []
current_world = None
hit_effects = []
main_character = None
merchant = None
quest_npc = None
camera_y = 0.0


def enter():
    # 게임 시작/초기화 시 호출되는 함수 (기존 setup_worlds 로직)
    global village_world, mine_world, mine_2_world, dungeon_world, boss_world, current_world
    global main_character, hit_effects, merchant, quest_npc
    global camera_y

    camera_y = 0.0
    main_character = Main_Character()

    village = Village()
    merchant = Merchant(800, 150)
    quest_npc = QuestNPC(400, 150)
    village_world = [village, merchant, quest_npc, main_character]

    mine = Mine()
    mine_world = [mine, main_character]

    mine_2 = Mine_2()
    mine_2_world = [mine_2, main_character]

    dungeon = Dungeon()
    dungeon_world = [dungeon, main_character]

    boss_stage = BossStage()
    boss_world = [boss_stage, main_character]

    current_world = village_world
    hit_effects = []


def exit():
    # 게임 종료/상태 변경 시 호출 (필요하면 메모리 정리)
    global main_character, current_world
    # main_character = None # 필요에 따라 초기화
    pass


def update():
    global current_world, hit_effects, camera_y
    global mine_world, dungeon_world, boss_world

    # [중요] 캐릭터 사망 체크 -> 게임 오버 상태로 전환
    if main_character.hp <= 0:
        game_framework.framework.change_state(game_over_state)
        return

    for o in current_world:
        if isinstance(o, (Mine, Mine_2, Mineral, Dungeon, BossStage)):
            o.update(main_character)
        else:
            o.update()

    hit_effects = [effect for effect in hit_effects if not effect.update()]

    # 마을 HP 회복
    if current_world == village_world:
        if get_time() - main_character.last_regen_time >= 1.0:
            if main_character.hp < main_character.max_hp:
                main_character.hp = min(main_character.max_hp, main_character.hp + 10)
            main_character.last_regen_time = get_time()
    else:
        main_character.last_regen_time = get_time()

    # 월드 전환 로직
    handle_world_change()

    # 충돌 체크 호출
    check_collisions()


def draw():
    global camera_y
    clear_canvas()

    for o in current_world:
        o.draw(camera_y)

    for effect in hit_effects:
        effect.draw(camera_y)

    main_character.inventory.draw()
    main_character.shop.draw(main_character)

    if quest_npc:
        quest_npc.draw_ui(main_character)

    update_canvas()


def handle_events():
    global merchant, quest_npc
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.framework.quit()

        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            click_x, click_y = event.x, 800 - 1 - event.y

            if main_character.shop.visible:
                main_character.shop.handle_event(event, main_character, merchant)
            else:
                if current_world == village_world:
                    if merchant and merchant.x - 50 <= click_x <= merchant.x + 50 and merchant.y - 50 <= click_y <= merchant.y + 50:
                        main_character.shop.toggle()
                    elif quest_npc and quest_npc.x - 50 <= click_x <= quest_npc.x + 50 and quest_npc.y - 50 <= click_y <= quest_npc.y + 50:
                        quest_npc.handle_interaction(main_character)

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                if main_character.shop.visible:
                    main_character.shop.visible = False
                elif main_character.inventory.visible:
                    main_character.inventory.visible = False
                else:
                    # ESC 누르면 게임 종료 or 타이틀로 이동 선택
                    game_framework.framework.quit()

            elif event.key == SDLK_e:
                main_character.inventory.toggle()
            # 광산 이동 키
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


def handle_world_change():
    global current_world, main_character, camera_y
    global mine_world, dungeon_world, boss_world

    # 1. 마을 -> 광산
    if current_world == village_world and main_character.x > 1200:
        mine_world = [Mine(), main_character]
        change_world(mine_world)
        main_character.x = 10;
        main_character.y = 150

    # 2. 광산 -> 마을
    elif current_world == mine_world and main_character.x < 0:
        change_world(village_world)
        main_character.x = 1190;
        main_character.y = 150

    # 3. 마을 -> 던전
    elif current_world == village_world and main_character.x < 0:
        dungeon_world = [Dungeon(), main_character]
        change_world(dungeon_world)
        main_character.x = 1190;
        main_character.y = 150

    # 4. 던전 -> 마을
    elif current_world == dungeon_world and main_character.x > 1200:
        change_world(village_world)
        main_character.x = 10;
        main_character.y = 150

    # 5. 던전 -> 보스방
    elif current_world == dungeon_world and main_character.x < 0:
        boss_world = [BossStage(), main_character]
        change_world(boss_world)
        main_character.x = 100;
        main_character.y = 150

    # 6. 보스방 -> 던전
    elif current_world == boss_world and main_character.x > 1200:
        dungeon_world = [Dungeon(), main_character]
        change_world(dungeon_world)
        main_character.x = 1190;
        main_character.y = 150

    if current_world == mine_2_world:
        target_camera_y = main_character.y - 300.0
        camera_y = min(0.0, target_camera_y)
        mine_2_map = mine_2_world[0]
        mine_2_map.procedural_update(camera_y)


def change_world(new_world):
    global current_world, camera_y
    camera_y = 0.0
    current_world = new_world
    main_character.clear_projectiles()
    hit_effects.clear()
    if new_world != mine_2_world:
        main_character.ground_y = 150
    if new_world in [village_world, mine_world, dungeon_world]:
        main_character.y = 150
        main_character.is_jumping = False
        main_character.jump_velocity = 0


def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


def check_collisions():
    global current_world, main_character

    # 충돌 로직은 기존 main.py 코드를 그대로 가져옵니다.
    # 내용이 길어서 생략하지 않고 핵심 구조만 보여드립니다.
    # (실제 파일에는 기존 main.py의 check_collisions 내용을 그대로 넣으세요)

    if current_world == mine_world:
        # ... 광산 충돌 코드 ...
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

    elif current_world == mine_2_world:
        # ... 광산2 충돌 코드 ...
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
                    if main_character.x < soil.x:
                        main_character.x -= overlap_x
                    else:
                        main_character.x += overlap_x
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

    elif current_world == dungeon_world:
        # ... 던전 충돌 코드 ...
        dungeon = dungeon_world[0]
        goblins_to_remove = []
        axes_to_remove = []
        for goblin in dungeon.goblins:
            if goblin.hp <= 0: continue
            if collide(main_character, goblin):
                if main_character.hit(10):
                    hit_effects.append(HitEffect(main_character.x, main_character.y))
        for axe in main_character.axes:
            for goblin in dungeon.goblins:
                if goblin.hp <= 0: continue
                if collide(axe, goblin) and goblin not in axe.hit_objects:
                    if goblin.hit(main_character.damage, main_character.face_dir):
                        if goblin not in goblins_to_remove:
                            goblins_to_remove.append(goblin)
                            main_character.goblin_kill_count += 1
                    hit_effects.append(HitEffect(goblin.x, goblin.y))
                    axe.hit_objects.append(goblin)
        for thrown_axe in main_character.thrown_axes:
            if thrown_axe in axes_to_remove: continue
            for goblin in dungeon.goblins:
                if goblin.hp <= 0: continue
                if collide(thrown_axe, goblin):
                    if goblin.hit(main_character.damage, thrown_axe.direction):
                        if goblin not in goblins_to_remove:
                            goblins_to_remove.append(goblin)
                            main_character.goblin_kill_count += 1
                    axes_to_remove.append(thrown_axe)
                    hit_effects.append(HitEffect(goblin.x, goblin.y))
                    break
        for goblin in goblins_to_remove:
            if goblin in dungeon.goblins: dungeon.goblins.remove(goblin)
        for thrown_axe in axes_to_remove:
            if thrown_axe in main_character.thrown_axes: main_character.thrown_axes.remove(thrown_axe)

    elif current_world == boss_world:
        # ... 보스 충돌 코드 ...
        boss_stage = boss_world[0]
        boss = boss_stage.boss
        if boss.hp > 0:
            if collide(main_character, boss):
                if main_character.hit(boss.damage):
                    hit_effects.append(HitEffect(main_character.x, main_character.y))
                    if main_character.x < boss.x:
                        main_character.x -= 50
                    else:
                        main_character.x += 50
            for arm in boss.arms:
                if collide(main_character, arm):
                    if main_character.hit(boss.damage):
                        hit_effects.append(HitEffect(main_character.x, main_character.y))
                        if main_character.x < arm.x:
                            main_character.x -= 30
                        else:
                            main_character.x += 30
            for axe in main_character.axes:
                if collide(axe, boss) and boss not in axe.hit_objects:
                    if boss.hit(main_character.damage):
                        main_character.boss_kill_count += 1
                        print("Boss Defeated! Kill Count:", main_character.boss_kill_count)
                    hit_effects.append(HitEffect(axe.x, axe.y))
                    axe.hit_objects.append(boss)
            axes_to_remove = []
            for thrown_axe in main_character.thrown_axes:
                if collide(thrown_axe, boss):
                    if boss.hit(main_character.damage):
                        main_character.boss_kill_count += 1
                        print("Boss Defeated!")
                    hit_effects.append(HitEffect(thrown_axe.x, thrown_axe.y))
                    axes_to_remove.append(thrown_axe)
                    break
            for axe in axes_to_remove:
                if axe in main_character.thrown_axes:
                    main_character.thrown_axes.remove(axe)