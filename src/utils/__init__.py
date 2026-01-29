"""Utilities for the ROMs Downloader."""

from .config import ConfigManager
from .constants import (
    APP_NAME,
    APP_VERSION,
    SYSTEMS,
    SYSTEMS_BY_MANUFACTURER,
    GENRES,
    REGIONS,
    RECOMMENDED_EMULATORS,
    DEFAULT_CONFIG,
)

__all__ = [
    "ConfigManager",
    "APP_NAME",
    "APP_VERSION",
    "SYSTEMS",
    "SYSTEMS_BY_MANUFACTURER",
    "GENRES",
    "REGIONS",
    "RECOMMENDED_EMULATORS",
    "DEFAULT_CONFIG",
]
