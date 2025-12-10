from pico2d import *
import game_framework
import play_state
import title_state

image = None
bg_image = None  # 배경 이미지 변수 추가


def enter():
    global image, bg_image
    # 게임오버 텍스트 이미지 로드
    image = load_image('gameover.png')

    # [추가] 검은색 배경 이미지 로드
    try:
        bg_image = load_image('black_bg.png')
    except:
        print("Failed to load black_bg.png")
        bg_image = None


def exit():
    global image, bg_image
    if image: del image
    if bg_image: del bg_image


def update():
    pass


def draw():
    clear_canvas()

    # 1. 검은 배경 먼저 그리기 (화면 꽉 채우기)
    if bg_image:
        bg_image.draw_to_origin(0, 0, 1200, 800)

    # 2. 게임오버 이미지 그리기 (화면 중앙)
    if image:
        image.draw(600, 400, 600, 400)

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.framework.quit()

        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.framework.quit()

        # 마우스 클릭 시 게임 재시작
        elif event.type == SDL_MOUSEBUTTONDOWN:
            game_framework.framework.change_state(play_state)