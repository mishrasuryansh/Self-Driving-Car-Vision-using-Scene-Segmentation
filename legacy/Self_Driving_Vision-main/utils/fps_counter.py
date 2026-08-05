import time

class FPSCounter:
    def __init__(self):
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

    def update(self):
        self.frame_count += 1
        now = time.time()
        if now - self.last_time >= 1.0:
            self.fps = self.frame_count / (now - self.last_time)
            self.frame_count = 0
            self.last_time = now

    def get_fps(self):
        return self.fps
