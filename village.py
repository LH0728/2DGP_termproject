from pico2d import load_image, get_time, load_font


class Village:
    def __init__(self):
        self.image = load_image('bg_near.png')
        self.image2 = load_image('bg_tower.png')
        self.image3 = load_image('grass.png')

        # 배경 이미지를 그릴 x 좌표들 (캐릭터 y축 150에 맞춰서)
        self.copy_x_positions = [0, 300, 600, 900, 1200]

        # image3를 image2 아래 빈 공간에 깔 x 좌표들
        self.ground_x_positions = [150, 450, 750, 1050]

    def draw(self, camera_y):
        # image3를 image2 아래쪽 빈 공간에 쭉 깔기 (y=100 아래 공간)
        for x_pos in self.ground_x_positions:
            self.image3.draw(x_pos, 50, 300, 115)

        self.image2.draw_to_origin(0, 100, 1200, 800)

        # image2 바로 위에 딱 붙여서 그리기 (y=100이 바닥이므로 그 위에 배치)
        for x_pos in self.copy_x_positions:
            self.image.draw(x_pos, 200, 300, 200)

    def update(self):
        pass

class Merchant:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = load_image('10201_T1.png')

        self.frame = 0
        self.timer = 0.0
        self.frame_count = 4
        self.anim_speed = 0.2
        self.width = self.image.w // self.frame_count
        self.height = self.image.h
        self.last_time = get_time()


    def update(self):

        now = get_time()
        dt = now - self.last_time
        self.last_time = now


        self.timer += dt
        if self.timer >= self.anim_speed:
            self.timer = 0
            self.frame = (self.frame + 1) % self.frame_count

    def draw(self, camera_y):
        draw_y = self.y - camera_y
        self.image.clip_draw(
            self.frame * self.width, 0, self.width, self.height,
            self.x, draw_y, 150, 150
        )


# [village.py] QuestNPC 클래스 전체 수정

class QuestNPC:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = load_image('10204_T1.png')

        self.frame = 0
        self.timer = 0.0
        self.frame_count = 4
        self.anim_speed = 0.2
        self.width = 60
        self.height = 60
        self.last_time = get_time()

        self.font = load_font('ENCR10B.TTF', 20)

        self.quest_index = 0
        self.is_started = False

        self.show_complete_msg = False
        self.complete_msg_timer = 0.0

        # [수정] 퀘스트 목록에 'type' 필드 추가 및 4번 퀘스트 추가
        self.quests = [
            # 1단계: 돌 수집
            {
                'type': 'collect', 'target': 1, 'count': 5, 'reward': 500,
                'title': "Quest 1: Stone Collector", 'desc': "Collect 5 Stones."
            },
            # 2단계: 은 수집
            {
                'type': 'collect', 'target': 2, 'count': 10, 'reward': 2000,
                'title': "Quest 2: Silver Rush", 'desc': "Collect 10 Silver."
            },
            # 3단계: 금 수집
            {
                'type': 'collect', 'target': 3, 'count': 10, 'reward': 5000,
                'title': "Quest 3: Gold Digger", 'desc': "Collect 10 Gold."
            },
            # 4단계: 고블린 사냥
            {
                'type': 'hunt', 'target': 'goblin', 'count': 15, 'reward': 10000,
                'title': "Quest 4: Goblin Slayer", 'desc': "Defeat 15 Goblins."
            }
        ]

    def update(self):
        now = get_time()
        dt = now - self.last_time
        self.last_time = now

        self.timer += dt
        if self.timer >= self.anim_speed:
            self.timer = 0
            self.frame = (self.frame + 1) % self.frame_count

        if self.show_complete_msg:
            self.complete_msg_timer += dt
            if self.complete_msg_timer >= 2.0:
                self.show_complete_msg = False
                self.complete_msg_timer = 0.0

    def draw(self, camera_y):
        draw_y = self.y - camera_y
        self.image.clip_draw(
            self.frame * self.width, 0, self.width, self.height,
            self.x, draw_y, 150, 150
        )

        if self.font:
            if self.quest_index >= len(self.quests):
                self.font.draw(self.x - 30, draw_y + 90, "All Clear!", (0, 255, 0))
            elif not self.is_started:
                self.font.draw(self.x, draw_y + 90, "!", (255, 0, 0))
            else:
                self.font.draw(self.x, draw_y + 90, "...", (255, 255, 255))

    def draw_ui(self, character):
        if not self.font: return

        if self.show_complete_msg:
            self.font.draw(500, 400, "QUEST COMPLETE!", (0, 255, 0))

        if not self.is_started or self.quest_index >= len(self.quests):
            return

        q = self.quests[self.quest_index]
        target_count = q['count']
        current_count = 0

        # [수정] 퀘스트 타입에 따라 현재 진행도 계산
        if q['type'] == 'collect':
            current_count = character.inventory.items.get(q['target'], 0)
        elif q['type'] == 'hunt':
            current_count = character.goblin_kill_count

        text_color = (255, 255, 255)
        if current_count >= target_count:
            text_color = (0, 255, 0)

        self.font.draw(800, 80, q['title'], (255, 255, 0))
        self.font.draw(800, 50, f"{q['desc']} ({current_count}/{target_count})", text_color)

    def handle_interaction(self, character):
        if self.quest_index >= len(self.quests):
            print("[Quest] 모든 의뢰를 완료했습니다.")
            return

        q = self.quests[self.quest_index]

        # 1. 퀘스트 시작 전이면 수락
        if not self.is_started:
            self.is_started = True

            # [추가] 사냥 퀘스트를 시작할 때, 현재까지 잡은 수를 기준으로 카운트하고 싶다면
            # 여기서 character.goblin_kill_count를 0으로 초기화할 수도 있습니다.
            # 지금은 "누적" 카운트로 진행합니다.

            print(f"[Quest 시작] {q['title']}을 수락했습니다!")
            return

        # 2. 퀘스트 진행 중 -> 완료 조건 확인
        is_clear = False

        if q['type'] == 'collect':
            item_id = q['target']
            needed = q['count']
            has = character.inventory.items.get(item_id, 0)
            if has >= needed:
                character.inventory.items[item_id] -= needed
                is_clear = True

        elif q['type'] == 'hunt':
            needed = q['count']
            has = character.goblin_kill_count
            if has >= needed:
                is_clear = True

        if is_clear:
            character.inventory.add_coin(q['reward'])
            print(f"[Quest 완료] {q['title']} 클리어! 보상: {q['reward']}코인")

            self.show_complete_msg = True
            self.complete_msg_timer = 0.0

            self.quest_index += 1
            self.is_started = False
        else:
            print(f"[Quest 진행중] 조건을 만족하지 못했습니다.")