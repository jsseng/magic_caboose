from default_pyglet_app import DefaultPygletApp
from serial_controller_input import ControllerEvent
import pyglet


class App(DefaultPygletApp):
    def __init__(self, *args, **kwargs):
        super().__init__(caption="Example App", *args, **kwargs)
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

    def on_draw(self):
        pyglet.gl.glFlush()
        self.clear()
        self.label.draw()
