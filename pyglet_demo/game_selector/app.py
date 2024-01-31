from typing import Tuple
from default_app import DefaultApp
import pyglet


class App(DefaultApp):
    def __init__(self, window_size: Tuple[int, int], apps, open_app):
        super().__init__(window_size)
        self.caption = "Game Selector"
        self.apps = apps
        self.open_app = open_app
        self.width = window_size[0]
        self.height = window_size[1]
        button_width, button_height = 200, 50
        self.buttons = [
            self.create_button(
                "Mode 1",
                (self.width // 2, self.height // 2 + 50),
                button_width,
                button_height,
            ),
            self.create_button(
                "Mode 2",
                (self.width // 2, self.height // 2 - 50),
                button_width,
                button_height,
            ),
        ]

    def create_button(self, label, position, width, height):
        button = pyglet.shapes.Rectangle(
            x=position[0] - width // 2,
            y=position[1] - height // 2,
            width=width,
            height=height,
            color=(0, 0, 255),
        )
        button.label = pyglet.text.Label(
            label,
            font_name="Arial",
            font_size=14,
            x=position[0],
            y=position[1],
            anchor_x="center",
            anchor_y="center",
            color=(255, 255, 255, 255),
        )
        return button

    def on_draw(self):
        # super().on_draw()
        for button in self.buttons:
            button.draw()
            button.label.draw()
