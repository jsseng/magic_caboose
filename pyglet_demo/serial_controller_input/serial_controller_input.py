import serial
import struct
from sys import platform, stderr
from socket import gethostname
from enum import Enum

BAUD_RATE = 115_200

DEV_FILE = "/dev/feather"

RED_BUTTON_NUM = 0
GREEN_BUTTON_NUM = 1

PACKET_HOLD_BIT_POS = 6
PACKET_NUM_CLICKS_POS = 4


def generate_button_packet(button_num: int, num_clicks: int = 1, hold: bool = False):
    return (
        (hold << PACKET_HOLD_BIT_POS)
        | (num_clicks & 0x3) << PACKET_NUM_CLICKS_POS
        | button_num
    )


class ControllerEvent(Enum):
    GREEN_SINGLE_CLICK = generate_button_packet(GREEN_BUTTON_NUM, 1)
    GREEN_DOUBLE_CLICK = generate_button_packet(GREEN_BUTTON_NUM, 2)
    GREEN_TRIPLE_CLICK = generate_button_packet(GREEN_BUTTON_NUM, 3)
    GREEN_SINGLE_LONG_CLICK = generate_button_packet(GREEN_BUTTON_NUM, 1, True)
    GREEN_DOUBLE_LONG_CLICK = generate_button_packet(GREEN_BUTTON_NUM, 2, True)
    GREEN_TRIPLE_LONG_CLICK = generate_button_packet(GREEN_BUTTON_NUM, 3, True)
    RED_SINGLE_CLICK = generate_button_packet(RED_BUTTON_NUM, 1)
    RED_DOUBLE_CLICK = generate_button_packet(RED_BUTTON_NUM, 2)
    RED_TRIPLE_CLICK = generate_button_packet(RED_BUTTON_NUM, 3)
    RED_SINGLE_LONG_CLICK = generate_button_packet(RED_BUTTON_NUM, 1, True)
    RED_DOUBLE_LONG_CLICK = generate_button_packet(RED_BUTTON_NUM, 2, True)
    RED_TRIPLE_LONG_CLICK = generate_button_packet(RED_BUTTON_NUM, 3, True)
    BATTERY_UPDATE = 0xA0


class ControllerInput:
    def __init__(self, on_controller_event=None, on_battery_change=None):
        if platform != "darwin" and gethostname() == "ubuntu":
            self.ser = serial.Serial(DEV_FILE, BAUD_RATE, timeout=0)
            print("Controller connected", file=stderr)
        else:
            self.ser = None
            print("Controller not detected", file=stderr)
        self.on_controller_event = self._check_and_call(on_controller_event)
        self.on_battery_change = self._check_and_call(on_battery_change)

    def _check_and_call(self, callback):
        if callback is not None:
            return callback
        return lambda *args: None

    def update(self):
        if self.ser is None:
            return
        data = self.ser.read(self.ser.in_waiting)
        if len(data) > 0:
            print(data, data[-1], len(data))
            last_byte = data[-1]
        if len(data) == 1:
            self.on_controller_event(ControllerEvent(last_byte))
        elif len(data) == 5:
            if data[0] == ControllerEvent.BATTERY_UPDATE.value:
                [battery_level] = struct.unpack("f", data[1:])
                self.on_battery_change(battery_level)
