import serial
import struct
from sys import platform, stderr
from socket import gethostname
from enum import Enum
from typing import Optional, Callable, Dict, Any
import atexit

BAUD_RATE = 115_200

DEV_FILE = "/dev/feather"

RED_BUTTON_NUM = 0
GREEN_BUTTON_NUM = 1
RED_GREEN_BUTTON_NUM = 2

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
    RED_GREEN_SINGLE_LONG_CLICK = generate_button_packet(RED_GREEN_BUTTON_NUM, 1, True)
    RED_GREEN_DOUBLE_LONG_CLICK = generate_button_packet(RED_GREEN_BUTTON_NUM, 2, True)
    RED_GREEN_TRIPLE_LONG_CLICK = generate_button_packet(RED_GREEN_BUTTON_NUM, 3, True)
    BATTERY_UPDATE = 0xA0
    ACCL_UPDATE = 0xA1


class ControllerInput:
    def __init__(
        self,
        on_controller_event: Optional[
            Callable[[ControllerEvent, Dict[str, Any]], None]
        ] = None,
        on_battery_change: Optional[Callable[[float], None]] = None,
    ):
        """_summary_

        Args:
            on_controller_event: function called on controller event.
            on_battery_change: function called battery change event.
        """
        if platform != "darwin" and gethostname() == "ubuntu":
            self.ser = serial.Serial(DEV_FILE, BAUD_RATE, timeout=0)
            print("Controller connected", file=stderr)
        elif platform == "darwin":
            try:
                dev_file = get_macos_devfile()
                if len(dev_file) == 0:
                    raise Exception("Could not find controller dev file")
                self.ser = serial.Serial(dev_file, BAUD_RATE, timeout=0)
                print("Controller connected", file=stderr)
            except Exception as e:
                self.ser = None
                print(f"{e}\nController not detected", file=stderr)
        else:
            self.ser = None
            print("Controller not detected", file=stderr)
        self._on_controller_event = self._check_and_call(on_controller_event)
        self._on_battery_change = self._check_and_call(on_battery_change)

        atexit.register(self._close)

    def _check_and_call(self, callback):
        if callback is not None:
            return callback
        return lambda *args, **kwargs: None

    def connected(self):
        return self.ser is not None

    def update(self):
        if self.ser is None:
            return
        data = self.ser.read(self.ser.in_waiting)
        if len(data) > 0:
            # print(data, data[-1], len(data))
            last_byte = data[-1]
        if len(data) == 1:
            # print(ControllerEvent(last_byte).name)
            self._on_controller_event(ControllerEvent(last_byte))
        elif len(data) == 5:
            if data[0] == ControllerEvent.BATTERY_UPDATE.value:
                [battery_level] = struct.unpack("f", data[1:])
                self._on_battery_change(battery_level)
        elif len(data) == 7:
            if data[0] == ControllerEvent.ACCL_UPDATE.value:
                accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = struct.unpack(
                    "bbbbbb", data[1:7]
                )
                self._on_controller_event(
                    ControllerEvent.ACCL_UPDATE,
                    **{
                        "accel_x": accel_x,
                        "accel_y": accel_y,
                        "accel_z": accel_z,
                        "gyro_x": gyro_x,
                        "gryo_y": gyro_y,
                        "gyro_z": gyro_z,
                    },
                )

    def _close(self):
        if self.ser is None:
            return
        else:
            print("Disconnected Controller", file=stderr)
            self.ser.close()


def get_macos_devfile():
    import subprocess

    command = "ioreg -r -c IOUSBHostDevice -n 'Feather M0' -l | grep -o '/dev/cu\.\w*'"  # noqa: W605, E501
    output = subprocess.check_output(command, shell=True, text=True)
    return output.strip()


if __name__ == "__main__":
    from datetime import datetime
    import time

    timestamp = ""

    def on_controller_event(event: ControllerEvent, **kwargs):
        print(f"{timestamp} {event.name} {kwargs}")

    controller_input = ControllerInput(on_controller_event=on_controller_event)

    interval = 1 / 60  # Interval in seconds for 60 Hz

    while True:
        start_time = time.time()

        # Call the function
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if controller_input.connected() is False:
            break
        controller_input.update()

        # Calculate the time taken for the function call
        elapsed_time = time.time() - start_time

        # If the function execution took less than the desired interval
        # sleep for the remaining time
        if elapsed_time < interval:
            time.sleep(interval - elapsed_time)
        else:
            print("Warning: Function execution time exceeds desired interval.")
