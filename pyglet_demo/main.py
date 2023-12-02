import pyglet
from sys import platform
from os import system
from socket import gethostname


import configs
import app
import serialInput


def main():
    gl_background_color = tuple(map(lambda x: x / 255.0, configs.BACKGROUND_COLOR))

    config = pyglet.gl.Config(sample_buffers=1, samples=8, double_buffer=True)
    window = pyglet.window.Window(
        caption="Caboose Wheel", config=config, fullscreen=True
    )
    pyglet.gl.glClearColor(*gl_background_color, 1.0)
    pyglet.options["audio"] = ("openal", "pulse", "directsound", "silent")

    game_app = app.App((window.width, window.height))

    @window.event
    def on_draw():
        pyglet.gl.glFlush()
        window.clear()

        game_app.on_draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        game_app.on_click(x, y, button)

    # dev board will need to be changed. not sure of the name in debian
    if platform != "darwin" and gethostname() == "ubuntu":
        serialInputHandler = serialInput.Input(
            game_app.spin,
            on_green_hold=pyglet.app.exit,
            on_red_hold=lambda: system("shutdown now"),
        )
    else:
        serialInputHandler = None

    def update_all(deltaTime):
        if serialInputHandler is not None:
            serialInputHandler.update()
        game_app.on_update(deltaTime)

    pyglet.clock.schedule_interval(update_all, 1 / 60)
    pyglet.app.run()


if __name__ == "__main__":
    main()
