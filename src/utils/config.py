"""Configuration management for the ROMs Downloader."""

import json
import os
from pathlib import Path
from typing import Any, Dict

from .constants import DEFAULT_CONFIG, CONFIG_FILE


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_dir: Path = None):
        """Initialize the config manager.

        Args:
            config_dir: Directory to store config file. Defaults to app directory.
        """
        if config_dir is None:
            config_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / CONFIG_FILE
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}

        # Merge with defaults for any missing keys
        for key, value in DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value

    def save(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key.
            value: Value to set.
        """
        self._config[key] = value

    def get_download_path(self) -> Path:
        """Get the download path as a Path object."""
        return Path(self.get("downloadPath", DEFAULT_CONFIG["downloadPath"]))

    def get_region_priority(self) -> list:
        """Get the region priority list."""
        return self.get("regionPriority", DEFAULT_CONFIG["regionPriority"])

    def is_disclaimer_accepted(self) -> bool:
        """Check if the legal disclaimer has been accepted."""
        return self.get("disclaimerAccepted", False)

    def accept_disclaimer(self) -> None:
        """Mark the legal disclaimer as accepted."""
        self.set("disclaimerAccepted", True)
        self.save()

    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config.copy()
