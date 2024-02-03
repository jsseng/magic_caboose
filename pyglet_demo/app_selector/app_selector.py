import pyglet
import sys
import pathlib
from threading import Timer
from os import system

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from serial_controller_input import ControllerEvent, ControllerInput  # noqa: E402


class App(pyglet.window.Window):
    name = "App Selector"

    def __init__(self, apps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyglet.options["audio"] = ("openal", "pulse", "directsound", "silent")
        self.controller_input = ControllerInput(self.on_controller_event)
        gl_background_color = tuple(map(lambda x: x / 255.0, (0, 0, 0)))
        pyglet.gl.glClearColor(*gl_background_color, 1.0)
        self.apps = apps
        self.label = pyglet.text.Label(
            "Select a Game",
            font_name="Arial",
            font_size=64,
            x=self.width // 2,
            y=self.height - 100,
            anchor_x="center",
            anchor_y="center",
        )
        button_width, button_height = 400, 100
        self.buttons = [
            self.create_button(
                self.apps[0],
                (self.width // 2, self.height // 2 + 75),
                button_width,
                button_height,
            ),
            self.create_button(
                self.apps[1],
                (self.width // 2, self.height // 2 - 75),
                button_width,
                button_height,
            ),
        ]
        self.shutdown_label = pyglet.text.Label(
            "Shutting down in 10s...Press red button or S on keyboard to stop shutdown.",
            font_name="Arial",
            font_size=24,
            x=0,
            y=self.height,
            anchor_x="left",
            # anchor_y="bottom",
            anchor_y="top",
            color=(255, 0, 0, 255),
        )
        self.selected_mode = 0
        self.select_mode(0)

        self.shutdown_timer = None
        pyglet.clock.schedule_interval(self.update_all, 1 / 60)
        pyglet.app.run()

    def update_all(self, delta_time):
        self.controller_input.update()

    def create_button(self, label, position, width, height):
        button = pyglet.shapes.BorderedRectangle(
            x=position[0] - width // 2,
            y=position[1] - height // 2,
            width=width,
            height=height,
            color=(0, 0, 255),
            border_color=(0, 0, 255),
            border=25,
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

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.select_mode(-1)
        elif symbol == pyglet.window.key.DOWN:
            self.select_mode(1)
        elif symbol == pyglet.window.key.ENTER:
            self.on_enter()
        elif symbol == pyglet.window.key.ESCAPE:
            self.exit()
        elif symbol == pyglet.window.key.S:
            self.handle_shutdown()

    def handle_shutdown(self, cancel_shutdown_only=False):
        if self.shutdown_timer is not None:
            self.shutdown_timer.cancel()
            self.shutdown_timer = None
        elif not cancel_shutdown_only:
            self.shutdown_timer = Timer(10, lambda: system("shutdown now"))
            self.shutdown_timer.start()

    def on_controller_event(self, event):
        event_handlers = {
            ControllerEvent.GREEN_SINGLE_CLICK: lambda: self.select_mode(1),
            ControllerEvent.GREEN_SINGLE_LONG_CLICK: self.on_enter,
            ControllerEvent.RED_SINGLE_LONG_CLICK: self.handle_shutdown,
            ControllerEvent.RED_SINGLE_CLICK: lambda: self.handle_shutdown(True),
        }
        if event in event_handlers:
            event_handlers[event]()

    def select_mode(self, direction):
        if self.selected_mode is not None:
            self.buttons[self.selected_mode].border_color = (
                0,
                0,
                255,
            )  # Reset color of the currently selected button

        self.selected_mode = (self.selected_mode + direction) % len(self.buttons)
        self.buttons[self.selected_mode].border_color = (
            255,
            255,
            255,
        )  # Highlight the newly selected button

    def on_enter(self):
        if self.selected_mode is not None:
            print(self.apps[self.selected_mode])
            self.exit()

    def on_draw(self):
        pyglet.gl.glFlush()
        self.clear()
        self.label.draw()
        for button in self.buttons:
            button.draw()
            button.label.draw()
        if self.shutdown_timer is not None:
            self.shutdown_label.draw()

    def exit(self):
        self.controller_input.close()
        pyglet.app.exit()


if __name__ == "__main__":
    default_config = pyglet.gl.Config(sample_buffers=1, samples=8, double_buffer=True)
    App(sys.argv[1:], caption="Game Selector", fullscreen=True, config=default_config)
