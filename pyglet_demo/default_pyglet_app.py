import pyglet
from typing import final
from default_app import DefaultApp


class DefaultPygletApp(pyglet.window.Window, DefaultApp):
    def __init__(self, *args, **kwargs):
        DefaultApp.__init__(self, *args, **kwargs)
        if "update_handlers" in kwargs:
            del kwargs["update_handlers"]
        default_config = pyglet.gl.Config(
            sample_buffers=1, samples=8, double_buffer=True
        )
        kwargs.setdefault("fullscreen", True)
        kwargs.setdefault("caption", "Default caption")
        kwargs.setdefault("config", default_config)

        super().__init__(*args, **kwargs)
        pyglet.options["audio"] = ("openal", "pulse", "directsound", "silent")

    def on_update(self, delta_time):
        pass

    def on_controller_event(self, event):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 4:
            self.exit()

    @final
    def update_all(self, delta_time):
        for updater in self.update_handlers:
            updater()
        self.on_update(delta_time)

    @final
    def start(self):
        pyglet.clock.schedule_interval(self.update_all, 1 / 60)
        pyglet.app.run()

    @final
    def exit(self):
        pyglet.app.exit()
