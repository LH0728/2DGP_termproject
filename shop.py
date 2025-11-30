from pico2d import *


class Shop:
    def __init__(self):
        self.visible = False
        self.slot_image = load_image('UI_BTN_Tier_1.png')

        try:
            self.font = load_font('ENCR10B.TTF', 20)
            self.title_font = load_font('ENCR10B.TTF', 30)
        except:
            self.font = None
            self.title_font = None

        self.center_x = 650
        self.center_y = 400


        self.items_3x3 = [None] * 9



        self.icons = {
            1: load_image('21203.png'),
            2: load_image('21204.png'),
            3: load_image('21205.png'),
            4: load_image('21206.png')
        }

        self.prices = {
            1: 10,  # Common
            2: 50,  # Uncommon
            3: 200,  # Rare
            4: 1000  # Legend
        }

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event, character, npc):
        if not self.visible:
            return False

        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            self.visible = False
            return True

        if event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            # 마우스 좌표 변환 (SDL은 좌상단 기준, Pico2D는 좌하단 기준)
            click_x, click_y = event.x, 800 - 1 - event.y

            # --- 슬롯 위치 계산 (draw 함수와 동일한 로직) ---
            slot_size = 80
            slot_margin = 10

            grid_start_y = self.center_y + 150

            # 플레이어 인벤토리 시작 위치 (하단 한 줄)
            row_start_x = self.center_x - (slot_size * 2 + slot_margin * 1.5)
            row_start_y = grid_start_y - (slot_size + slot_margin) * 3 - 40

            # 4개의 슬롯을 순회하며 클릭 확인
            for j in range(4):
                mineral_type = j + 1  # 1, 2, 3, 4

                # 각 슬롯의 중심 좌표
                slot_x = row_start_x + j * (slot_size + slot_margin)
                slot_y = row_start_y

                # 충돌 박스 계산 (중심 기준 w/2, h/2)
                l = slot_x - slot_size / 2
                r = slot_x + slot_size / 2
                b = slot_y - slot_size / 2
                t = slot_y + slot_size / 2

                # 클릭이 슬롯 안에 들어왔는지 확인
                if l <= click_x <= r and b <= click_y <= t:
                    # 보유 수량 확인
                    if character.inventory.items.get(mineral_type, 0) > 0:
                        # 1. 아이템 차감
                        character.inventory.items[mineral_type] -= 1
                        # 2. 돈 지급
                        price = self.prices[mineral_type]
                        character.inventory.add_coin(price)
                        print(f"[판매 성공] 광물 {mineral_type}번 -> {price} 코인 획득!")
                    else:
                        print(f"[판매 실패] {mineral_type}번 광물이 없습니다.")

                    return True  # 클릭 처리 완료

        return False


    def draw(self, character):
        if not self.visible:
            return


        if self.title_font:
            self.title_font.draw(self.center_x-80, self.center_y + 300, "SHOP", (255, 255, 255))

        slot_size = 80
        slot_margin = 10
        item_icon_size = 50

        grid_start_x = self.center_x - (slot_size * 1.5 + slot_margin * 1)
        grid_start_y = self.center_y + 150

        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                slot_x = grid_start_x + j * (slot_size + slot_margin)
                slot_y = grid_start_y - i * (slot_size + slot_margin)

                self.slot_image.draw(slot_x, slot_y, slot_size, slot_size)


                item = self.items_3x3[idx]
                if item and item['type'] in self.icons:
                    self.icons[item['type']].draw(slot_x, slot_y, item_icon_size, item_icon_size)
                    if self.font and item['count'] is not None:
                        self.font.draw(slot_x + 15, slot_y - 25, f"{item['count']}", (255, 255, 0))

        row_start_x = self.center_x - (slot_size * 2 + slot_margin * 1.5)
        row_start_y = grid_start_y - (slot_size + slot_margin) * 3 - 40


        for j in range(4):
            mineral_type = j + 1  # 1, 2, 3, 4

            slot_x = row_start_x + j * (slot_size + slot_margin)
            slot_y = row_start_y

            self.slot_image.draw(slot_x, slot_y, slot_size, slot_size)

            if mineral_type in self.icons:
                # 아이콘 그리기
                self.icons[mineral_type].draw(slot_x, slot_y, item_icon_size, item_icon_size)


                count = character.inventory.items.get(mineral_type, 0)
                if self.font:

                    self.font.draw(slot_x + 15, slot_y - 25, f"{count}", (255, 255, 0))