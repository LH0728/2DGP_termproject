import math

from pico2d import *


class Axe:
    image = None

    # 애니메이션 및 스윙 관련 상수
    NUM_FRAMES = 5
    FRAME_DURATION = 0.04
    ANIMATION_DURATION = NUM_FRAMES * FRAME_DURATION

    # 스윙 궤적 설정: 머리 위(90도)에서 시작하여 시계방향으로 90도 회전 -> 0도(오른쪽)에서 종료
    SWING_RADIUS = 50  # 스윙 반경 (캐릭터 중심으로부터의 거리)
    START_ANGLE_RAD = math.radians(90)  # 시작 각도 (머리 위)
    END_ANGLE_RAD = math.radians(0)  # 종료 각도 (오른쪽)
    TOTAL_ANGLE_RAD = END_ANGLE_RAD - START_ANGLE_RAD # -90도 만큼 회전

    # 회전 중심 오프셋 (캐릭터 중심 기준)
    PIVOT_OFFSET_X = 10  # 앞쪽으로
    PIVOT_OFFSET_Y = -20 # 아래쪽으로

    def __init__(self, parent):
        if not Axe.image:
            Axe.image = load_image('10001_T1_Pickax.png')

        self.parent = parent
        self.start_time = get_time()
        self.frame = 0
        self.angle_rad = 0  # 현재 곡괭이의 회전 각도

        # 초기 위치 계산 (update에서 매번 갱신됨)
        self.x, self.y = 0, 0

    def update(self):
        elapsed_time = get_time() - self.start_time

        # 애니메이션이 끝나면 True 반환 (삭제 신호)
        if elapsed_time >= Axe.ANIMATION_DURATION:
            return True

        # 진행률 계산 (0.0 ~ 1.0)
        progress = elapsed_time / Axe.ANIMATION_DURATION

        # 현재 스윙 각도 계산
        self.angle_rad = Axe.START_ANGLE_RAD + Axe.TOTAL_ANGLE_RAD * progress

        # 회전 중심을 캐릭터 중심에서 살짝 이동
        pivot_x = self.parent.x + Axe.PIVOT_OFFSET_X * self.parent.face_dir
        pivot_y = self.parent.y + Axe.PIVOT_OFFSET_Y

        # 회전 중심으로부터의 곡괭이 위치 계산
        if self.parent.face_dir == 1:  # 오른쪽
            self.x = pivot_x + Axe.SWING_RADIUS * math.cos(self.angle_rad)
            self.y = pivot_y + Axe.SWING_RADIUS * math.sin(self.angle_rad)
        else:  # 왼쪽
            # 왼쪽을 볼 때는 각도를 뒤집어 계산
            mirrored_angle = math.pi - self.angle_rad
            self.x = pivot_x + Axe.SWING_RADIUS * math.cos(mirrored_angle)
            self.y = pivot_y + Axe.SWING_RADIUS * math.sin(mirrored_angle)

        # 이미지 프레임 업데이트
        self.frame = int(progress * Axe.NUM_FRAMES) % Axe.NUM_FRAMES

        return False

    def draw(self, camera_y):
        # 프레임에 맞는 이미지 클리핑
        frame_x = self.frame * 30

        # 오른쪽을 기준으로 그리기 각도 계산
        # (곡괭이 날이 스윙 방향을 향하도록 45도 정도 빼줍니다)
        base_draw_angle = self.angle_rad - math.radians(45)
        draw_y = self.y - camera_y
        # 캐릭터 방향에 따라 이미지 회전 및 반전 적용
        if self.parent.face_dir == 1:  # 오른쪽
            Axe.image.clip_composite_draw(frame_x, 0, 30, 24, base_draw_angle, '', self.x, draw_y, 100, 100)
        else:  # 왼쪽
            # 왼쪽을 볼 때는 오른쪽 각도를 반전시키고, 이미지를 수평으로 뒤집습니다.
            mirrored_draw_angle = -base_draw_angle
            Axe.image.clip_composite_draw(frame_x, 0, 30, 24, mirrored_draw_angle, 'h', self.x, draw_y, 100, 100)

        l, b, r, t = self.get_bb()
        draw_rectangle(l, b - camera_y, r, t - camera_y)

    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50


class ThrownAxe:
    image = None
    SPEED_PPS = 700  # 초당 700 픽셀 속도
    ROTATION_SPEED_RPS = 2  # 초당 2바퀴 회전
    LIFETIME_S = 1.5  # 1.5초 후 소멸

    def __init__(self, x, y, direction):
        if ThrownAxe.image is None:
            ThrownAxe.image = load_image('10001_T1_Pickax.png')

        self.x, self.y = x, y
        self.direction = direction
        self.angle_rad = 0
        self.spawn_time = get_time()
        self.last_time = self.spawn_time

    def update(self):
        # 생존 시간 체크
        if get_time() - self.spawn_time > ThrownAxe.LIFETIME_S:
            return True  # True를 반환하여 삭제 신호 보냄

        # 경과 시간 계산
        now = get_time()
        dt = now - self.last_time
        self.last_time = now

        # 수평 이동
        self.x += ThrownAxe.SPEED_PPS * self.direction * dt

        # 회전
        self.angle_rad += ThrownAxe.ROTATION_SPEED_RPS * 2 * math.pi * dt

        return False  # 계속 업데이트

    def draw(self, camera_y):
        draw_y = self.y - camera_y
        ThrownAxe.image.clip_composite_draw(0, 0, 30, 24, self.angle_rad, '', self.x, draw_y, 100, 100)  # [수정]

        l, b, r, t = self.get_bb()
        draw_rectangle(l, b - camera_y, r, t - camera_y)

    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50
