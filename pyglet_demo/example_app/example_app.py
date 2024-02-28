import pyglet
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from serial_controller_input import ControllerEvent, ControllerInput  # noqa: E402


class App(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller_input = ControllerInput(self.on_controller_event)
        pyglet.options["audio"] = ("openal", "pulse", "directsound", "silent")
        gl_background_color = tuple(map(lambda x: x / 255.0, (0, 0, 255)))
        pyglet.gl.glClearColor(*gl_background_color, 1.0)
        self.label = pyglet.text.Label(
            "Default App",
            font_name="Arial",
            font_size=100,
            x=self.width / 2,
            y=self.height / 2,
            anchor_x="center",
            anchor_y="center",
            color=(255, 0, 0, 255),
        )

        pyglet.clock.schedule_interval(self.update_all, 1 / 60)
        pyglet.app.run()

    def update_all(self, delta_time):
        self.controller_input.update()

    def on_controller_event(self, event):
        if event == ControllerEvent.RED_SINGLE_CLICK:
            self.exit()

    def on_draw(self):
        pyglet.gl.glFlush()
        self.clear()
        self.label.draw()

    def on_close(self):
        pyglet.app.exit()

    def exit(self):
        self.on_close()


if __name__ == "__main__":
    default_config = pyglet.gl.Config(sample_buffers=1, samples=8, double_buffer=True)
    App(caption="Example App", fullscreen=True, config=default_config)
