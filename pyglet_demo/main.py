import pyglet
from sys import platform
from os import system
from socket import gethostname

from threading import Timer

from magic_caboose import MagicCaboose
from default_app import DefaultApp
from game_selector import GameSelector
from serial_controller_input import ControllerEvent, ControllerInput

BACKGROUND_COLOR = (150, 200, 250)


def main():
    config = pyglet.gl.Config(sample_buffers=1, samples=8, double_buffer=True)
    window = pyglet.window.Window(
        caption="Caboose Wheel", config=config, fullscreen=True
    )
    pyglet.options["audio"] = ("openal", "pulse", "directsound", "silent")

    cur_game_idx = 0
    apps = [
        GameSelector((window.width, window.height), [], None),
        DefaultApp((window.width, window.height)),
        MagicCaboose((window.width, window.height)),
    ]

    cur_app = apps[cur_game_idx]
    cur_app.on_startup()

    shut_down_timer = None

    shutdown_label = pyglet.text.Label(
        "Shutting down in 10s...Press red to stop shutdown.",
        font_name="Arial",
        font_size=24,
        x=0,
        y=window.height,
        anchor_x="left",
        # anchor_y="bottom",
        anchor_y="top",
        color=(255, 0, 0, 255),
    )

    def handle_app_change(new_game: DefaultApp):
        nonlocal cur_app
        cur_app = new_game
        new_game.on_startup()

    def handle_next_app():
        nonlocal cur_game_idx
        cur_game_idx = (cur_game_idx + 1) % len(apps)
        handle_app_change(apps[cur_game_idx])

    @window.event
    def on_draw():
        pyglet.gl.glFlush()
        window.clear()

        cur_app.on_draw()
        if shut_down_timer is not None:
            shutdown_label.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        nonlocal cur_game_idx, cur_app
        if button == 2:
            handle_shutdown()
        elif button == 4:
            handle_next_app()
            # cur_game_idx = (cur_game_idx + 1) % len(games)
            # handle_game_change(games[cur_game_idx])
            # pyglet.app.exit()
        else:
            cur_app.on_click(x, y, button)

    def handle_shutdown(cancel_shutdown_only=False):
        nonlocal shut_down_timer
        if shut_down_timer is not None:
            shut_down_timer.cancel()
            shut_down_timer = None
        elif not cancel_shutdown_only:
            shut_down_timer = Timer(10, lambda: system("shutdown now"))
            shut_down_timer.start()

    def handle_controller_event(event):
        event_handlers_dict = {
            ControllerEvent.GREEN_SINGLE_LONG_CLICK: pyglet.app.exit,
            ControllerEvent.RED_SINGLE_LONG_CLICK: handle_shutdown,
            ControllerEvent.RED_SINGLE_CLICK: lambda: handle_shutdown(
                cancel_shutdown_only=True
            ),
            ControllerEvent.RED_DOUBLE_CLICK: handle_next_app,
        }
        if event in event_handlers_dict:
            # some events are handled at top level
            event_handlers_dict[event]()
        else:
            cur_app.on_controller_event(event)

    # dev board will need to be changed. not sure of the name in debian
    if platform != "darwin" and gethostname() == "ubuntu":
        serialInputHandler = ControllerInput(
            on_controller_event=handle_controller_event
        )
    else:
        serialInputHandler = None

    def update_all(deltaTime):
        if serialInputHandler is not None:
            serialInputHandler.update()
        cur_app.on_update(deltaTime)

    pyglet.clock.schedule_interval(update_all, 1 / 60)
    pyglet.app.run()


if __name__ == "__main__":
    main()
