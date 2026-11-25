import json
import subprocess

from pathlib import Path

BASE_DIR = Path(__file__).parent

CONFIG_PATH = BASE_DIR / "config.json"

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

RUNNER = str(BASE_DIR / CONFIG["runner_path"])
MODEL = str(BASE_DIR / CONFIG["model_path"])
TOKENIZER = str(BASE_DIR / CONFIG["tokenizer_path"])
TIMEOUT = CONFIG["timeout"]


def generate_guidance(data):

    defects = data.get("defects", [])

    inspection = {

        "status": data.get("status"),

        "severity": data.get("severity"),

        "count": data.get("count", 0),

        "defects": defects
    }

    prompt = (
        "You are an industrial PCB inspection assistant. "
        "Explain the inspection result using only the provided "
        "inspection data. Do not invent measurements or defect "
        "locations. Do not change the inspection decision. "
        "Provide a brief explanation and safe operator follow-up. "
        "If severity is CRITICAL, recommend holding the board "
        "for qualified review. Guidance is advisory only. "
        "Inspection data: "
        + json.dumps(inspection, separators=(",", ":"))
    )

    try:

        command = [
            RUNNER,
            "--model_path", MODEL,
            "--tokenizer_path", TOKENIZER,
            "--prompt", prompt
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=True
        )

        output = result.stdout.strip()

        if output:
            return output

        return "LLM returned an empty response."

    except subprocess.TimeoutExpired:

        return "LLM response timed out."

    except Exception as exc:

        print("LLM error:", exc)

        return (
            "LLM guidance unavailable. "
            "Follow the original inspection decision "
            "and qualified PCB inspection procedures."
        )