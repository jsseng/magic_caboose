import pyglet
from typing import final
from default_app import DefaultApp


class DefaultPygletApp(pyglet.window.Window, DefaultApp):
    def __init__(self, *args, **kwargs):
        """A class all pyglet apps should inherit from.
        Creates pyglet window.

        Keywords arguments:
            all arguments supported by pyglet.window.Window
                (Hover over super().__init__ to see supported args)
            update_handers (list): passed to DefaultApp
        """
        DefaultApp.__init__(self, *args, **kwargs)
        if "update_handlers" in kwargs:
            del kwargs["update_handlers"]
        default_config = pyglet.gl.Config(
            sample_buffers=1, samples=8, double_buffer=True
        )
        kwargs.setdefault("fullscreen", False)
        kwargs.setdefault("caption", "Default caption")
        kwargs.setdefault("config", default_config)

        super().__init__(*args, **kwargs)
        pyglet.options["audio"] = ("openal", "pulse", "directsound", "silent")

        self.count = 0
        self.event_loop = None

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

        if self.count == 100:
            print(f"{self.name} updating")
            self.count = 0

        self.count += 1

    @final
    def start(self):
        pyglet.clock.schedule_interval(self.update_all, 1 / 60)
        # self.event_loop = pyglet.app.EventLoop()
        # self.event_loop.run()
        pyglet.app.run()

    def on_close(self):
        pyglet.clock.unschedule(self.update_all)
        return super().on_close()

    @final
    def exit(self):
        print(f"{self.name} exiting")
        pyglet.clock.unschedule(self.update_all)
        # self.event_loop.exit()
        self.close()
        pyglet.app.exit()
