import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULTS = {
    "interval_minutes": 30,
}


class Settings:
    def __init__(self):
        self.data = DEFAULTS.copy()
        self.load()

    def load(self) -> None:
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    saved = json.load(f)
                self.data.update(saved)
            except (json.JSONDecodeError, OSError):
                # If the file is corrupted or unreadable, fall back to defaults
                pass

    def save(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key: str):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value) -> None:
        self.data[key] = value
        self.save()