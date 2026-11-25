import json
import time

import serial

from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

SERIAL_PORT = CONFIG["serial_port"]
BAUDRATE = CONFIG["baudrate"]

ser = None


def initialize_serial():

    global ser

    if ser is not None and ser.is_open:
        return True

    try:

        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            timeout=0.1,
            write_timeout=0.5
        )

        time.sleep(0.2)

        print("UART initialized:", SERIAL_PORT)

        return True

    except Exception as exc:

        print("UART initialization failed:", exc)

        ser = None

        return False


def send_inspection(payload):

    global ser

    if not initialize_serial():
        return False

    try:

        message = json.dumps(
            payload,
            separators=(",", ":")
        ) + "\n"

        ser.write(message.encode("utf-8"))

        ser.flush()

        print("Inspection message transmitted")

        return True

    except Exception as exc:

        print("UART transmission error:", exc)

        try:
            ser.close()
        except Exception:
            pass

        ser = None

        return False


def close_serial():

    global ser

    if ser is not None:

        try:
            ser.close()
        except Exception:
            pass

        ser = None