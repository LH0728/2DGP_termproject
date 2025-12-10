from pico2d import load_image, get_time


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


# [village.py] 기존 코드 아래에 추가
from pico2d import *


# ... (기존 Village, Merchant 클래스 유지) ...

class QuestNPC:
    def __init__(self, x, y):
        self.x, self.y = x, y
        # 제공해주신 이미지 로드
        self.image = load_image('10204_T1.png')

        # 애니메이션 관련 변수
        self.frame = 0
        self.timer = 0.0
        self.frame_count = 4
        self.anim_speed = 0.2

        # 이미지 크기: 240x60 -> 프레임당 60x60
        self.width = 60
        self.height = 60
        self.last_time = get_time()

        # 퀘스트 상태 (0: 시작 전, 1: 진행 중, 2: 완료)
        self.quest_step = 0

        # 대화 폰트
        try:
            self.font = load_font('ENCR10B.TTF', 16)
        except:
            self.font = None

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

        # 캐릭터 그리기 (약간 확대 2.5배)
        self.image.clip_draw(
            self.frame * self.width, 0, self.width, self.height,
            self.x, draw_y, 150, 150
        )

        # 머리 위에 퀘스트 상태 표시 (텍스트)
        if self.font:
            if self.quest_step == 0:
                self.font.draw(self.x - 20, draw_y + 90, "!", (255, 0, 0))  # 느낌표
            elif self.quest_step == 1:
                self.font.draw(self.x - 60, draw_y + 90, "Bring 5 Stones", (255, 255, 255))
            elif self.quest_step == 2:
                self.font.draw(self.x - 40, draw_y + 90, "Thanks!", (0, 255, 0))

    def handle_interaction(self, character):
        # 퀘스트 로직 처리
        if self.quest_step == 0:
            print("[Quest] 퀘스트 수락: 1번 광물(회색) 5개를 구해오세요!")
            self.quest_step = 1

        elif self.quest_step == 1:
            # 인벤토리 확인 (1번 광물 키값은 1)
            required_item = 1
            required_count = 5

            current_count = character.inventory.items.get(required_item, 0)

            if current_count >= required_count:
                # 아이템 차감 및 보상 지급
                character.inventory.items[required_item] -= required_count
                character.inventory.add_coin(1000)
                print(f"[Quest] 퀘스트 완료! 보상: 1000코인 (남은 광물: {character.inventory.items[required_item]}개)")
                self.quest_step = 2
            else:
                print(f"[Quest] 아직 부족합니다. (현재: {current_count}/5)")

        elif self.quest_step == 2:
            print("[Quest] 이미 퀘스트를 완료했습니다.")