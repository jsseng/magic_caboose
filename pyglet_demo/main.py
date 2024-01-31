import pyglet
from sys import platform
from os import system
from socket import gethostname

from threading import Timer

from magic_caboose import MagicCaboose
from example_app import ExampleApp
from default_app import DefaultApp

# from default_app import DefaultApp
# from game_selector import GameSelector
from app_selector import AppSelector
from serial_controller_input import ControllerEvent, ControllerInput
from typing import Optional

BACKGROUND_COLOR = (150, 200, 250)

APPS = [MagicCaboose, ExampleApp]


import gc


def main():
    def handle_serial_update():
        if serial_input_handler is not None:
            serial_input_handler.update()

    def handle_controller_event(event):
        event_handlers_dict = {
            ControllerEvent.GREEN_SINGLE_LONG_CLICK: lambda: print("foo"),
        }
        if event in event_handlers_dict:
            # some events are handled at top level
            event_handlers_dict[event]()
        else:
            pass
            # cur_app.on_controller_event(event)

    # dev board will need to be changed. not sure of the name in debian
    if platform != "darwin" and gethostname() == "ubuntu":
        serial_input_handler = ControllerInput(
            on_controller_event=handle_controller_event
        )
    else:
        serial_input_handler = None
    # import time

    def open_app(app_class):
        nonlocal next_app_class
        next_app_class = app_class

    next_app_class = AppSelector
    cur_app = None

    while next_app_class is not None:
        gc.collect()
        if next_app_class == AppSelector:
            cur_app = next_app_class(
                APPS, open_app, update_handlers=[handle_serial_update]
            )
            next_app_class = AppSelector
        else:
            cur_app = next_app_class(update_handlers=[handle_serial_update])
            next_app_class = AppSelector
        cur_app.start()

    # def handle_shutdown(cancel_shutdown_only=False):
    #     nonlocal shut_down_timer
    #     if shut_down_timer is not None:
    #         shut_down_timer.cancel()
    #         shut_down_timer = None
    #     elif not cancel_shutdown_only:
    #         shut_down_timer = Timer(10, lambda: system("shutdown now"))
    #         shut_down_timer.start()

    # cur_app.start()


if __name__ == "__main__":
    main()
