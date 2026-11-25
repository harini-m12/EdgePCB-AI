import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

SEVERITY_RULES = CONFIG["severity_rules"]
REWORKABLE_CLASSES = CONFIG["reworkable_classes"]

PRIORITY = {
    "NONE": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}


def evaluate_defects(defects):

    evaluated = []

    for item in defects:

        name = item["name"]

        severity = SEVERITY_RULES.get(
            name, "UNKNOWN"
        )

        repairability = (
            "REWORKABLE"
            if name in REWORKABLE_CLASSES
            else "NON-REWORKABLE"
        )

        evaluated.append({
            "name": name,
            "confidence": float(item["confidence"]),
            "severity": severity,
            "repairability": repairability
        })

    valid_severities = [
        item["severity"]
        for item in evaluated
        if item["severity"] in PRIORITY
    ]

    if not valid_severities:

        overall_severity = "NONE"

    else:

        overall_severity = max(
            valid_severities,
            key=lambda x: PRIORITY[x]
        )

    return evaluated, overall_severity