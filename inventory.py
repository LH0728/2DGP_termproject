from pico2d import *


class Inventory:
    def __init__(self):
        self.items = {
            1: 0,  # Common
            2: 0,  # Uncommon
            3: 0,  # Rare
            4: 0  # Legend
        }
        self.visible = False

        self.bg_image = load_image('UI_BTN_Tier_1.png')

        # 아이콘 표시를 위해 광물 이미지 로드 (크기 조절은 draw에서)
        self.icons = {
            1: load_image('21203.png'),
            2: load_image('21204.png'),
            3: load_image('21205.png'),
            4: load_image('21206.png')
        }

        # 텍스트 출력을 위한 폰트 (프로젝트 폴더에 폰트 파일이 있어야 함)
        try:
            self.font = load_font('ENCR10B.TTF', 30)
        except:
            self.font = None  # 폰트 없으면 오류 방지

    def add(self, item_type):
        if item_type in self.items:
            self.items[item_type] += 1
            print(f"아이템 획득: {item_type}번 광물 (현재 {self.items[item_type]}개)")

    def toggle(self):
        self.visible = not self.visible

    def draw(self):
        if not self.visible:
            return

        start_x = 400
        y = 400


        for i, (item_type, count) in enumerate(self.items.items()):
            # 아이콘 그리기 (x좌표를 150씩 띄워서 배치)
            icon_x = start_x + (i * 150)
            self.bg_image.draw(icon_x, y, 100, 100)
            self.icons[item_type].draw(icon_x, y, 50, 50)

            # 수량 표시
            if self.font and count >= 0:
                self.font.draw(icon_x + 10, y - 25, f'{count}', (255, 255, 0))