"""Download model for the ROMs Downloader."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class DownloadStatus(Enum):
    """Download status enumeration."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Download:
    """Represents a download task."""

    id: int = 0
    game_id: int = 0
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""

    # Joined from games table
    title: str = ""
    system_id: str = ""
    download_url: str = ""
    file_name: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Download":
        """Create a Download from a dictionary."""
        status_str = data.get("status", "pending")
        try:
            status = DownloadStatus(status_str)
        except ValueError:
            status = DownloadStatus.PENDING

        return cls(
            id=data.get("id", 0),
            game_id=data.get("game_id", 0),
            status=status,
            progress=data.get("progress", 0.0),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message", ""),
            title=data.get("title", ""),
            system_id=data.get("system_id", ""),
            download_url=data.get("download_url", ""),
            file_name=data.get("file_name", ""),
        )

    @property
    def is_active(self) -> bool:
        """Check if the download is active."""
        return self.status in (DownloadStatus.PENDING, DownloadStatus.DOWNLOADING)

    @property
    def status_text(self) -> str:
        """Get a human-readable status text."""
        status_map = {
            DownloadStatus.PENDING: "Queued",
            DownloadStatus.DOWNLOADING: f"Downloading ({self.progress:.0f}%)",
            DownloadStatus.COMPLETED: "Completed",
            DownloadStatus.FAILED: f"Failed: {self.error_message}",
            DownloadStatus.PAUSED: "Paused",
        }
        return status_map.get(self.status, "Unknown")
