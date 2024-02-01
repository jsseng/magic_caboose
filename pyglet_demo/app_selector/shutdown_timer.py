from threading import Timer
from os import system

SHUTDOWN_COUNTDOWN_TIME = 10  # 10s


class ShutdownTimer:
    def __init__(self) -> None:
        self.started = False

    def start(self):
        self.timer = Timer(SHUTDOWN_COUNTDOWN_TIME, lambda: system("shutdown now"))
        self.timer.start()
        self.started = True

    def cancel(self):
        if self.started:
            self.timer.cancel()
            self.started = False
