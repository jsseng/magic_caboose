import serial
import struct
import sys
from os import system
from enum import Enum

BAUD_RATE = 115_200

DEV_FILE = "/dev/feather"


class ControllerEvent(Enum):
    GREEN_CLICK = 0x10
    RED_CLICK = 0x20
    BATTERY_UPDATE = 0x30
    RED_HOLD = 0x40
    GREEN_HOLD = 0x50
    RED_DOUBLE_CLICK = 0x60
    GREEN_DOUBLE_CLICK = 0x70


class ControllerInput:
    def __init__(self, on_controller_event=None, on_battery_change=None):
        self.ser = serial.Serial(DEV_FILE, BAUD_RATE, timeout=0)
        self.on_controller_event = self._check_and_call(on_controller_event)
        self.on_battery_change = self._check_and_call(on_battery_change)

    def _check_and_call(self, callback):
        if callback is not None:
            return callback
        return lambda *args: None

    def update(self):
        data = self.ser.read(self.ser.in_waiting)
        if len(data) > 0:
            print(data, data[-1], len(data))
            last_byte = data[-1]
        if len(data) == 1:
            self.on_controller_event(last_byte)
        elif len(data) == 5:
            if data[0] == ControllerEvent.BATTERY_UPDATE:
                [battery_level] = struct.unpack("f", data[1:])
                self.on_battery_change(battery_level)
