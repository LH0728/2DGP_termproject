from pico2d import *
import game_framework
import play_state

# 전역 변수 선언
white_bg_image = None
title_image = None
font = None


def enter():
    global white_bg_image, title_image, font

    # 1. 배경으로 쓸 1x1 흰색 이미지 로드 (필수)
    # 이 파일이 프로젝트 폴더에 있어야 합니다.
    try:
        white_bg_image = load_image('white_bg.png')
    except:
        print("ERROR: cannot load white_bg.png")
        # 만약 파일이 없으면 임시로 아무거나 로드해서 에러 방지 (실제로는 꼭 넣어주세요)
        # white_bg_image = load_image('character.png')
        pass

    # 2. 타이틀 메인 이미지 로드
    # 'title.png' 파일이 준비되면 주석을 해제하고 사용하세요.
    try:
        title_image = load_image('title.png')
    except:
        title_image = None  # 파일 없으면 텍스트로 대체

    # 폰트 로드
    try:
        font = load_font('ENCR10B.TTF', 50)
    except:
        font = None


def exit():
    global white_bg_image, title_image, font
    if white_bg_image: del white_bg_image
    if title_image: del title_image
    if font: del font


def update():
    pass


def draw():
    clear_canvas()  # 기본 버퍼 비우기

    # [중요] 1. 흰색 배경 먼저 그리기
    # 1x1 이미지를 화면 전체(1200x800)로 늘려서 그립니다.
    if white_bg_image:
        white_bg_image.draw_to_origin(0, 0, 1200, 800)

    # [중요] 2. 그 위에 타이틀 이미지 그리기
    if title_image:
        title_image.draw(600, 400)  # 화면 중앙에 배치
    else:
        # 타이틀 이미지가 없을 경우 텍스트 출력 (배경이 흰색이니 글씨는 검은색으로)
        if font:
            font.draw(350, 450, "PRESS SPACE OR CLICK", (0, 0, 0))
            font.draw(450, 350, "TO START GAME", (0, 0, 0))

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.framework.quit()

        # 스페이스바나 마우스 클릭 시 게임 시작
        elif (event.type == SDL_KEYDOWN and event.key == SDLK_SPACE) or \
                (event.type == SDL_MOUSEBUTTONDOWN):
            game_framework.framework.change_state(play_state)