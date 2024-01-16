from typing import Tuple
import pyglet


class DefaultApp:
    def __init__(self, window_size: Tuple[int, int]):
        self.window_size = window_size
        self.caption = "Default caption"

    def on_startup(self):
        gl_background_color = tuple(map(lambda x: x / 255.0, (0, 0, 0)))
        pyglet.gl.glClearColor(*gl_background_color, 1.0)

    def on_draw(self):
        pass

    def on_click(self, x, y, button):
        pass

    def on_mouse_press(self, x, y, button):
        pass

    def on_controller_event(self, event):
        pass

    def on_update(self, deltaTime):
        pass
