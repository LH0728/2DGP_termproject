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

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event, character, npc):
        if not self.visible:
            return False

        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            self.visible = False
            return True

        if event.type == SDL_MOUSEBUTTONDOWN:

            pass

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