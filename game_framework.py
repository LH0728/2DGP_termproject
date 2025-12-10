import time

class GameFramework:
    def __init__(self):
        self.running = True
        self.stack = []

    def change_state(self, state):
        if len(self.stack) > 0:
            self.stack[-1].exit()
            self.stack.pop()
        self.stack.append(state)
        state.enter()

    def push_state(self, state):
        if len(self.stack) > 0:
            self.stack[-1].pause()
        self.stack.append(state)
        state.enter()

    def pop_state(self):
        if len(self.stack) > 0:
            self.stack[-1].exit()
            self.stack.pop()
        if len(self.stack) > 0:
            self.stack[-1].resume()

    def quit(self):
        self.running = False

    def run(self, start_state):
        self.change_state(start_state)
        while self.running:
            self.stack[-1].handle_events()
            self.stack[-1].update()
            self.stack[-1].draw()
            time.sleep(0.01)

# 전역 프레임워크 객체 (어디서든 import해서 사용 가능)
framework = GameFramework()