import os
import json
from pathlib import Path

DEFAULT_BASE_URL = "https://eyay.afdaan.web.id/v1"
DEFAULT_API_KEY = "sk-8e3b65f406c3bd98-a0ejmb-62ab1e83"
DEFAULT_MODEL = "ag/gemini-3.7-flash-high"
DEFAULT_MODE = "build"  # Modes: 'plan', 'build', 'ask'

CONFIG_DIR = Path.home() / ".yncli"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    config = {
        "base_url": os.getenv("YNCLI_BASE_URL", DEFAULT_BASE_URL),
        "api_key": os.getenv("YNCLI_API_KEY", DEFAULT_API_KEY),
        "model": os.getenv("YNCLI_MODEL", DEFAULT_MODEL),
        "mode": os.getenv("YNCLI_MODE", DEFAULT_MODE),
        "temperature": 0.2,
        "max_tokens": 16384,
        "auto_validate_syntax": True,
        "show_thinking": False,
        "auto_approve": False,
        "theme": "minimal-dark",
    }

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config.update(saved)
        except Exception:
            pass

    return config


def save_config(updates: dict) -> None:
    config = load_config()
    config.update(updates)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
