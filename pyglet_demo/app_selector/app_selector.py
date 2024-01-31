from default_pyglet_app import DefaultPygletApp
from serial_controller_input import ControllerEvent
import pyglet


class App(DefaultPygletApp):
    def __init__(self, apps, open_app, *args, **kwargs):
        super().__init__(caption="Game Selector", *args, **kwargs)
        gl_background_color = tuple(map(lambda x: x / 255.0, (0, 0, 0)))
        pyglet.gl.glClearColor(*gl_background_color, 1.0)
        self.apps = apps
        self.open_app = open_app
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
                "Mode 1",
                (self.width // 2, self.height // 2 + 75),
                button_width,
                button_height,
            ),
            self.create_button(
                "Mode 2",
                (self.width // 2, self.height // 2 - 75),
                button_width,
                button_height,
            ),
        ]
        self.shutdown_label = pyglet.text.Label(
            "Shutting down in 10s...Press red to stop shutdown.",
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

    def on_controller_event(self, event):
        event_handlers = {
            ControllerEvent.GREEN_SINGLE_CLICK: lambda: self.select_mode(1)
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
            print(f"Selected Game Mode: Mode {self.selected_mode + 1}")
            # self.close()  # Close the current window
            # new_window = GameModeSelector(400, 300, resizable=True)  # Create a new window
            # pyglet.app.exit()  # Exit the current Pyglet application
            # pyglet.app.run()  # Start the new Pyglet application

    def on_draw(self):
        pyglet.gl.glFlush()
        self.clear()
        self.label.draw()
        for button in self.buttons:
            button.draw()
            button.label.draw()
