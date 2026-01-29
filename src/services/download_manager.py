"""Download manager for the ROMs Downloader."""

import os
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional
from queue import Queue, Empty

from PyQt6.QtCore import QObject, pyqtSignal

from .myrient import MyrientClient
from .file_organizer import FileOrganizer
from ..database.db_manager import DatabaseManager
from ..models import Download, DownloadStatus
from ..utils.config import ConfigManager


class DownloadWorker(QObject):
    """Worker for downloading files in a separate thread."""

    progress = pyqtSignal(int, float)  # download_id, progress percentage
    completed = pyqtSignal(int, str)  # download_id, file_path
    failed = pyqtSignal(int, str)  # download_id, error message
    started = pyqtSignal(int)  # download_id

    def __init__(
        self,
        myrient_client: MyrientClient,
        file_organizer: FileOrganizer,
        db_manager: DatabaseManager
    ):
        super().__init__()
        self.myrient_client = myrient_client
        self.file_organizer = file_organizer
        self.db_manager = db_manager
        self._queue: Queue = Queue()
        self._running = False
        self._current_download: Optional[Download] = None
        self._cancel_current = False

    def start(self) -> None:
        """Start the download worker."""
        self._running = True
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the download worker."""
        self._running = False
        self._cancel_current = True
        self._queue.put(None)  # Signal to stop

    def add_download(self, download: Download) -> None:
        """Add a download to the queue."""
        self._queue.put(download)

    def cancel_current(self) -> None:
        """Cancel the current download."""
        self._cancel_current = True

    def _process_queue(self) -> None:
        """Process downloads from the queue."""
        while self._running:
            try:
                download = self._queue.get(timeout=1)
                if download is None:
                    break

                self._cancel_current = False
                self._current_download = download
                self._process_download(download)
                self._current_download = None
            except Empty:
                continue

    def _process_download(self, download: Download) -> None:
        """Process a single download."""
        self.started.emit(download.id)
        self.db_manager.update_download_status(download.id, "downloading", 0)

        # Get the game info
        game = self.db_manager.get_game_by_id(download.game_id)
        if not game:
            self.failed.emit(download.id, "Game not found in database")
            self.db_manager.update_download_status(
                download.id, "failed", 0, "Game not found"
            )
            return

        # Create temp download path
        temp_dir = self.file_organizer.get_temp_dir()
        temp_path = temp_dir / game["file_name"]

        def progress_callback(downloaded: int, total: int) -> None:
            if self._cancel_current:
                raise InterruptedError("Download cancelled")
            if total > 0:
                progress = (downloaded / total) * 100
                self.progress.emit(download.id, progress)
                self.db_manager.update_download_status(
                    download.id, "downloading", progress
                )

        try:
            # Download the file with automatic fallback to alternatives
            success, final_url = self.myrient_client.download_with_fallback(
                game["download_url"],
                str(temp_path),
                game["system_id"],
                game["file_name"],
                progress_callback
            )

            if not success:
                raise Exception("Download failed - no working sources found")

            # Organize the file
            final_path = self.file_organizer.organize_file(
                temp_path,
                game["system_id"],
                game["title"],
                game.get("region", "Unknown")
            )

            # Add to library
            self.db_manager.add_to_library(download.game_id, str(final_path))
            self.db_manager.update_download_status(download.id, "completed", 100)
            self.completed.emit(download.id, str(final_path))

        except InterruptedError:
            # Clean up cancelled download
            if temp_path.exists():
                temp_path.unlink()
            self.db_manager.update_download_status(
                download.id, "failed", 0, "Cancelled"
            )
            self.failed.emit(download.id, "Download cancelled")

        except Exception as e:
            error_msg = str(e)
            self.db_manager.update_download_status(
                download.id, "failed", 0, error_msg
            )
            self.failed.emit(download.id, error_msg)
            # Clean up failed download
            if temp_path.exists():
                temp_path.unlink()


class DownloadManager(QObject):
    """Manages the download queue and workers."""

    download_started = pyqtSignal(int)  # download_id
    download_progress = pyqtSignal(int, float)  # download_id, progress
    download_completed = pyqtSignal(int, str)  # download_id, file_path
    download_failed = pyqtSignal(int, str)  # download_id, error message
    queue_updated = pyqtSignal()

    def __init__(
        self,
        db_manager: DatabaseManager,
        config_manager: ConfigManager
    ):
        super().__init__()
        self.db_manager = db_manager
        self.config_manager = config_manager

        self.myrient_client = MyrientClient()
        self.file_organizer = FileOrganizer(config_manager)

        self._workers: List[DownloadWorker] = []
        self._max_concurrent = config_manager.get("maxConcurrentDownloads", 2)

    def start(self) -> None:
        """Start the download manager."""
        for _ in range(self._max_concurrent):
            worker = DownloadWorker(
                self.myrient_client,
                self.file_organizer,
                self.db_manager
            )
            worker.started.connect(self._on_download_started)
            worker.progress.connect(self._on_download_progress)
            worker.completed.connect(self._on_download_completed)
            worker.failed.connect(self._on_download_failed)
            worker.start()
            self._workers.append(worker)

        # Resume any pending downloads
        self._resume_pending()

    def stop(self) -> None:
        """Stop all download workers."""
        for worker in self._workers:
            worker.stop()
        self._workers.clear()

    def add_download(self, game_id: int) -> int:
        """Add a game to the download queue.

        Args:
            game_id: ID of the game to download.

        Returns:
            Download ID.
        """
        download_id = self.db_manager.add_download(game_id)
        downloads = self.db_manager.get_pending_downloads()

        # Find the download we just added
        for dl in downloads:
            if dl["id"] == download_id:
                download = Download.from_dict(dl)
                # Distribute to workers round-robin
                worker_idx = download_id % len(self._workers)
                self._workers[worker_idx].add_download(download)
                break

        self.queue_updated.emit()
        return download_id

    def remove_download(self, download_id: int) -> None:
        """Remove a download from the queue."""
        self.db_manager.remove_download(download_id)
        self.queue_updated.emit()

    def get_queue(self) -> List[Download]:
        """Get all downloads in the queue."""
        downloads = self.db_manager.get_all_downloads()
        return [Download.from_dict(dl) for dl in downloads]

    def clear_completed(self) -> None:
        """Clear completed downloads from the queue."""
        self.db_manager.clear_completed_downloads()
        self.queue_updated.emit()

    def _resume_pending(self) -> None:
        """Resume any pending downloads from the database."""
        pending = self.db_manager.get_pending_downloads()
        for dl in pending:
            download = Download.from_dict(dl)
            worker_idx = download.id % len(self._workers)
            self._workers[worker_idx].add_download(download)

    def _on_download_started(self, download_id: int) -> None:
        """Handle download started signal."""
        self.download_started.emit(download_id)
        self.queue_updated.emit()

    def _on_download_progress(self, download_id: int, progress: float) -> None:
        """Handle download progress signal."""
        self.download_progress.emit(download_id, progress)

    def _on_download_completed(self, download_id: int, file_path: str) -> None:
        """Handle download completed signal."""
        self.download_completed.emit(download_id, file_path)
        self.queue_updated.emit()

    def _on_download_failed(self, download_id: int, error: str) -> None:
        """Handle download failed signal."""
        self.download_failed.emit(download_id, error)
        self.queue_updated.emit()
