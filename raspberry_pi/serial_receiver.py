
# ============================================================
# EDGEPCB-AI
# RASPBERRY PI 4 UART RECEIVER
#
# Receives inspection data from PYNQ-Z2
# Generates AI guidance
# Saves inspection data into SQLite
# ============================================================

import serial
import json
import time
import os

from database import initialize_database, save_inspection
from llm_service import generate_guidance


# ============================================================
# CONFIGURATION
# ============================================================

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "config.json"
)

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

SERIAL_PORT = CONFIG.get(
    "serial_port",
    "/dev/serial0"
)

BAUDRATE = CONFIG.get(
    "baudrate",
    115200
)

# ============================================================
# MESSAGE VALIDATION
# ============================================================

def validate_message(data):

    if not isinstance(data, dict):

        return False

    required_fields = [
        "id",
        "status",
        "severity",
        "count",
        "defects"
    ]

    for field in required_fields:

        if field not in data:

            print("[INVALID] Missing field:", field)

            return False

    if not isinstance(data["defects"], list):

        return False

    if not isinstance(data["count"], int):

        return False

    if data["count"] != len(data["defects"]):

        print("[INVALID] Defect count mismatch")

        return False

    for defect in data["defects"]:

        if not isinstance(defect, dict):

            return False

        if "name" not in defect:

            return False

        if "conf" not in defect:

            return False

        if "severity" not in defect:

            return False

        if "repairability" not in defect:

            return False

    return True


# ============================================================
# PROCESS INSPECTION
# ============================================================

def process_inspection(data):

    print("\n--------------------------------")

    print("[INSPECTION RECEIVED]")

    print(
        json.dumps(
            data,
            indent=2
        )
    )

    print("--------------------------------")

    # --------------------------------------------
    # AI GUIDANCE
    # --------------------------------------------

    try:

        guidance = generate_guidance(data)

    except Exception as e:

        print("[LLM ERROR]", e)

        guidance = (
            "AI guidance unavailable. "
            "Review the PCB inspection manually."
        )

    # --------------------------------------------
    # SAVE TO DATABASE
    # --------------------------------------------

    try:

        save_inspection(
            data,
            guidance
        )

        print("[DATABASE] Inspection saved.")

    except Exception as e:

        print("[DATABASE ERROR]", e)

    # --------------------------------------------
    # DISPLAY GUIDANCE
    # --------------------------------------------

    print("\n[OPERATOR GUIDANCE]")

    print(guidance)

    print("--------------------------------")


# ============================================================
# UART RECEIVER
# ============================================================

def receive_loop():

    while True:

        try:

            print(
                "[UART] Connecting to",
                SERIAL_PORT
            )

            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUDRATE,
                timeout=1
            )

            print("[UART] Connected.")

            while True:

                line = ser.readline()

                if not line:

                    continue

                try:

                    message = line.decode(
                        "utf-8"
                    ).strip()

                    if not message:

                        continue

                    data = json.loads(message)

                    if validate_message(data):

                        process_inspection(data)

                    else:

                        print(
                            "[INVALID MESSAGE]",
                            message
                        )

                except json.JSONDecodeError:

                    print(
                        "[JSON ERROR] Invalid JSON:",
                        line
                    )

                except UnicodeDecodeError:

                    print(
                        "[UART ERROR] Invalid encoding"
                    )

                except Exception as e:

                    print(
                        "[PROCESS ERROR]",
                        e
                    )

        except serial.SerialException as e:

            print(
                "[UART CONNECTION ERROR]",
                e
            )

            time.sleep(3)

        except Exception as e:

            print(
                "[RECEIVER ERROR]",
                e
            )

            time.sleep(3)

        finally:

            try:

                if "ser" in locals() and ser.is_open:

                    ser.close()

            except Exception:

                pass


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("======================================")

    print(" EDGEPCB-AI RASPBERRY PI RECEIVER")

    print("======================================")

    receive_loop()
