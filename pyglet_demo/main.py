import pyglet
from sys import platform
from os import system
from socket import gethostname

from threading import Timer

from magic_caboose import MagicCaboose
from example_app import ExampleApp

# from default_app import DefaultApp
# from game_selector import GameSelector
from app_selector import AppSelector
from serial_controller_input import ControllerEvent, ControllerInput

BACKGROUND_COLOR = (150, 200, 250)


def main():
    def handle_serial_update():
        if serial_input_handler is not None:
            serial_input_handler.update()

    # cur_app = AppSelector(
    #     [], lambda: print("nothing"), update_handlers=[handle_serial_update]
    # )
    cur_app = MagicCaboose(update_handlers=[handle_serial_update])
    # cur_app = ExampleApp(update_handlers=[handle_serial_update])

    # def handle_shutdown(cancel_shutdown_only=False):
    #     nonlocal shut_down_timer
    #     if shut_down_timer is not None:
    #         shut_down_timer.cancel()
    #         shut_down_timer = None
    #     elif not cancel_shutdown_only:
    #         shut_down_timer = Timer(10, lambda: system("shutdown now"))
    #         shut_down_timer.start()

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

    cur_app.start()


if __name__ == "__main__":
    main()
