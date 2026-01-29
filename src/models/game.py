"""Game model for the ROMs Downloader."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Game:
    """Represents a game/ROM in the catalog."""

    id: int = 0
    ia_identifier: str = ""
    title: str = ""
    system_id: str = ""
    genre: str = ""
    game_type: str = ""
    publisher: str = ""
    developer: str = ""
    release_year: Optional[int] = None
    region: str = ""
    description: str = ""
    file_size: int = 0
    file_name: str = ""
    file_hash: str = ""
    download_url: str = ""
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        """Create a Game from a dictionary."""
        return cls(
            id=data.get("id", 0),
            ia_identifier=data.get("ia_identifier", ""),
            title=data.get("title", ""),
            system_id=data.get("system_id", ""),
            genre=data.get("genre", ""),
            game_type=data.get("game_type", ""),
            publisher=data.get("publisher", ""),
            developer=data.get("developer", ""),
            release_year=data.get("release_year"),
            region=data.get("region", ""),
            description=data.get("description", ""),
            file_size=data.get("file_size", 0),
            file_name=data.get("file_name", ""),
            file_hash=data.get("file_hash", ""),
            download_url=data.get("download_url", ""),
            created_at=data.get("created_at"),
        )

    def to_dict(self) -> dict:
        """Convert the Game to a dictionary."""
        return {
            "id": self.id,
            "ia_identifier": self.ia_identifier,
            "title": self.title,
            "system_id": self.system_id,
            "genre": self.genre,
            "game_type": self.game_type,
            "publisher": self.publisher,
            "developer": self.developer,
            "release_year": self.release_year,
            "region": self.region,
            "description": self.description,
            "file_size": self.file_size,
            "file_name": self.file_name,
            "file_hash": self.file_hash,
            "download_url": self.download_url,
        }

    @property
    def display_size(self) -> str:
        """Get a human-readable file size."""
        if self.file_size == 0:
            return "Unknown"

        size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


@dataclass
class LibraryEntry:
    """Represents a game in the user's library."""

    id: int = 0
    game_id: int = 0
    file_path: str = ""
    downloaded_at: Optional[datetime] = None
    last_played: Optional[datetime] = None
    is_favorite: bool = False

    # Joined from games table
    title: str = ""
    system_id: str = ""
    genre: str = ""
    region: str = ""
    file_size: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "LibraryEntry":
        """Create a LibraryEntry from a dictionary."""
        return cls(
            id=data.get("id", 0),
            game_id=data.get("game_id", 0),
            file_path=data.get("file_path", ""),
            downloaded_at=data.get("downloaded_at"),
            last_played=data.get("last_played"),
            is_favorite=data.get("is_favorite", False),
            title=data.get("title", ""),
            system_id=data.get("system_id", ""),
            genre=data.get("genre", ""),
            region=data.get("region", ""),
            file_size=data.get("file_size", 0),
        )
