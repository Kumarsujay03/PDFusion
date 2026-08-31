"""Configuration manager for the application."""
import json
import os
from pathlib import Path
from typing import Any


class ConfigManager:
    """Manages application configuration with JSON persistence."""

    _instance = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._config_dir = Path(__file__).parent
        self._settings_file = self._config_dir / "settings.json"
        self._user_settings_file = self._get_user_settings_path()
        self._settings: dict[str, Any] = {}
        self._load()

    @staticmethod
    def _get_user_settings_path() -> Path:
        """Get user-specific settings path."""
        app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
        user_dir = Path(app_data) / "PDFusion"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "settings.json"

    def _load(self) -> None:
        """Load settings from default and user files."""
        # Load defaults
        if self._settings_file.exists():
            with open(self._settings_file, "r", encoding="utf-8") as f:
                self._settings = json.load(f)

        # Override with user settings
        if self._user_settings_file.exists():
            with open(self._user_settings_file, "r", encoding="utf-8") as f:
                user_settings = json.load(f)
                self._deep_merge(self._settings, user_settings)

    def _deep_merge(self, base: dict, override: dict) -> None:
        """Deep merge override into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting by dot-notation key (e.g., 'theme.mode')."""
        keys = key.split(".")
        value = self._settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a setting by dot-notation key."""
        keys = key.split(".")
        target = self._settings
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self._save_user_settings()

    def _save_user_settings(self) -> None:
        """Save current settings to user file."""
        with open(self._user_settings_file, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=4)

    def reset(self) -> None:
        """Reset to default settings."""
        if self._user_settings_file.exists():
            self._user_settings_file.unlink()
        self._settings = {}
        self._load()

    @property
    def settings(self) -> dict[str, Any]:
        """Get the full settings dictionary."""
        return self._settings.copy()
