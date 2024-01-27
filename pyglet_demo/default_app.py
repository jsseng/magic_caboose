from typing import Tuple
import pyglet


class DefaultApp:
    def __init__(self, window_size: Tuple[int, int]):
        self.window_size = window_size
        self.caption = "Default caption"
        self.label = pyglet.text.Label(
            "Default App",
            font_name="Arial",
            font_size=100,
            x=window_size[0] / 2,
            y=window_size[1] / 2,
            anchor_x="center",
            anchor_y="center",
            color=(255, 0, 0, 255),
        )

    def on_startup(self):
        gl_background_color = tuple(map(lambda x: x / 255.0, (0, 0, 0)))
        pyglet.gl.glClearColor(*gl_background_color, 1.0)

    def on_draw(self):
        self.label.draw()

    def on_click(self, x, y, button):
        pass

    def on_mouse_press(self, x, y, button):
        pass

    def on_controller_event(self, event):
        pass

    def on_update(self, deltaTime):
        pass
