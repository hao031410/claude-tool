"""Configuration management for dlna skill.

Config is stored in the skill directory under .dlna/config.json
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


# Get the skill directory (where this file is located)
def _get_skill_dir() -> Path:
    """Get the skill root directory."""
    return Path(__file__).parent.parent.parent


def _get_config_dir() -> Path:
    """Get the config directory (inside skill directory)."""
    config_dir = _get_skill_dir() / ".dlna"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def _get_config_file() -> Path:
    """Get the config file path."""
    return _get_config_dir() / "config.json"


@dataclass
class DLNAConfig:
    """DLNA skill configuration."""

    default_device: Optional[str] = None

    def save(self) -> None:
        """Save config to file."""
        config_file = _get_config_file()
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls) -> "DLNAConfig":
        """Load config from file."""
        config_file = _get_config_file()
        if not config_file.exists():
            return cls()

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, TypeError):
            return cls()


def get_default_device() -> Optional[str]:
    """Get the default device name."""
    config = DLNAConfig.load()
    return config.default_device


def set_default_device(device_name: str) -> None:
    """Set the default device name."""
    config = DLNAConfig.load()
    config.default_device = device_name
    config.save()


def clear_default_device() -> None:
    """Clear the default device."""
    config = DLNAConfig.load()
    config.default_device = None
    config.save()


def show_config() -> None:
    """Print current configuration."""
    config = DLNAConfig.load()
    config_file = _get_config_file()

    print(f"Config file: {config_file}")
    print()

    if config.default_device:
        print(f"Default device: {config.default_device}")
    else:
        print("Default device: (not set)")
