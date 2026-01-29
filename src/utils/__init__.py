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
    MULTI_SYSTEM_COLLECTIONS,
    SYSTEM_SEARCH_KEYWORDS,
)
from .games_database import (
    GAMES_DATABASE,
    get_games_for_system,
    get_all_games,
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
    "MULTI_SYSTEM_COLLECTIONS",
    "SYSTEM_SEARCH_KEYWORDS",
    "GAMES_DATABASE",
    "get_games_for_system",
    "get_all_games",
]
