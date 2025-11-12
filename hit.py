from pico2d import *

class HitEffect:
    image = None
    LIFETIME_S = 0.2  # 이펙트가 화면에 표시될 시간 (초)

    def __init__(self, x, y):
        if HitEffect.image is None:
            HitEffect.image = load_image('Hit_10.png')
        self.x, self.y = x, y
        self.spawn_time = get_time()

    def update(self):
        """
        이펙트의 생존 시간을 체크하고, 시간이 다 되면 True를 반환하여
        자신을 제거해야 함을 알립니다.
        """
        if get_time() - self.spawn_time > HitEffect.LIFETIME_S:
            return True  # 삭제 신호
        return False # 아직 활성 상태

    def draw(self):
        """
        이펙트 이미지를 그립니다.
        """
        # 이미지를 살짝 크게 그려서 잘 보이게 합니다.
        self.image.draw(self.x, self.y, 100, 100)


