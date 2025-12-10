from pico2d import *
from boss import Yormungand


class BossStage:
    def __init__(self):
        self.bg_image = load_image('bg6_boss.png')
        # 보스 생성 (위치값은 boss.py 내부에서 1800으로 재설정됨)
        self.boss = Yormungand(1100, 280)

    def update(self, character):
        self.boss.update(character)

    def draw(self, camera_y):
        # 배경 그리기
        self.bg_image.draw_to_origin(0, 0, 1200, 800)

        # [수정] 체력이 0이어도(죽어도) 퇴장 애니메이션을 보여줘야 하므로 조건문 삭제
        # if self.boss.hp > 0:  <-- 이 줄을 삭제했습니다.
        self.boss.draw(camera_y)