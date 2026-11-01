"""Load project settings from config/assumptions.yaml."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(name="assumptions.yaml"):
    with open(ROOT / "config" / name, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)
