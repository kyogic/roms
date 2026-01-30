"""Downloads view for managing the download queue."""

from typing import Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView, QProgressBar, QLabel
)
from PyQt6.QtCore import Qt

from ..services import DownloadManager
from ..models import Download, DownloadStatus
from ..utils import SYSTEMS


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_speed(speed_bytes: float) -> str:
    """Format bytes/sec to human readable speed."""
    if speed_bytes == 0:
        return "0 B/s"
    for unit in ["B/s", "KB/s", "MB/s", "GB/s"]:
        if speed_bytes < 1024:
            return f"{speed_bytes:.1f} {unit}"
        speed_bytes /= 1024
    return f"{speed_bytes:.1f} TB/s"


def format_eta(seconds: int) -> str:
    """Format seconds to human readable time."""
    if seconds <= 0:
        return "--:--"
    if seconds > 86400:  # More than a day
        return ">1 day"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


class DownloadProgressWidget(QWidget):
    """Widget displaying download progress with speed and ETA."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximumHeight(16)
        layout.addWidget(self.progress_bar)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(self.info_label)

    def set_progress(self, value: float, downloaded: int = 0, total: int = 0,
                     speed: float = 0, eta: int = 0) -> None:
        """Set the progress value with speed and ETA."""
        self.progress_bar.setValue(int(value))

        if total > 0 and speed > 0:
            info_text = f"{format_size(downloaded)}/{format_size(total)} | {format_speed(speed)} | ETA: {format_eta(eta)}"
            self.info_label.setText(info_text)
        elif total > 0:
            self.info_label.setText(f"{format_size(downloaded)}/{format_size(total)}")
        else:
            self.info_label.setText("")

    def set_status(self, status: DownloadStatus) -> None:
        """Set the display based on status."""
        if status == DownloadStatus.COMPLETED:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Completed")
            self.info_label.setText("")
        elif status == DownloadStatus.FAILED:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Failed")
            self.info_label.setText("")
        elif status == DownloadStatus.PENDING:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Queued")
            self.info_label.setText("")
        elif status == DownloadStatus.PAUSED:
            self.progress_bar.setFormat("Paused")
        else:
            self.progress_bar.setFormat("%p%")


class DownloadsView(QWidget):
    """Widget for managing downloads."""

    def __init__(self, download_manager: DownloadManager):
        super().__init__()
        self.download_manager = download_manager
        self._progress_widgets: Dict[int, DownloadProgressWidget] = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the downloads view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Control buttons
        btn_layout = QHBoxLayout()

        self.clear_completed_btn = QPushButton("Clear Completed")
        btn_layout.addWidget(self.clear_completed_btn)

        self.clear_all_btn = QPushButton("Clear All")
        btn_layout.addWidget(self.clear_all_btn)

        btn_layout.addStretch()

        self.status_label = QLabel("No downloads")
        btn_layout.addWidget(self.status_label)

        layout.addLayout(btn_layout)

        # Downloads table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Title", "System", "Status", "Progress", "Actions"
        ])

        # Table settings
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 250)  # Wider for speed/ETA info
        self.table.setColumnWidth(4, 80)

        layout.addWidget(self.table)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self.clear_completed_btn.clicked.connect(self._clear_completed)
        self.clear_all_btn.clicked.connect(self._clear_all)

        # Download manager signals
        self.download_manager.download_started.connect(self._on_download_started)
        self.download_manager.download_progress.connect(self._on_download_progress)
        self.download_manager.download_completed.connect(self._on_download_completed)
        self.download_manager.download_failed.connect(self._on_download_failed)
        self.download_manager.queue_updated.connect(self.refresh)

    def refresh(self) -> None:
        """Refresh the downloads table."""
        downloads = self.download_manager.get_queue()
        self._progress_widgets.clear()

        self.table.setRowCount(len(downloads))

        active_count = 0
        for row, download in enumerate(downloads):
            # Title
            title_item = QTableWidgetItem(download.title)
            title_item.setData(Qt.ItemDataRole.UserRole, download)
            self.table.setItem(row, 0, title_item)

            # System
            system = SYSTEMS.get(download.system_id)
            system_abbr = system.abbreviation if system else download.system_id.upper()
            self.table.setItem(row, 1, QTableWidgetItem(system_abbr))

            # Status
            self.table.setItem(row, 2, QTableWidgetItem(download.status.value.title()))

            # Progress
            progress_widget = DownloadProgressWidget()
            progress_widget.set_progress(download.progress)
            progress_widget.set_status(download.status)
            self.table.setCellWidget(row, 3, progress_widget)
            self._progress_widgets[download.id] = progress_widget

            # Actions
            if download.is_active:
                active_count += 1
                action_btn = QPushButton("Cancel")
                action_btn.clicked.connect(
                    lambda checked, d=download: self._cancel_download(d)
                )
            else:
                action_btn = QPushButton("Remove")
                action_btn.clicked.connect(
                    lambda checked, d=download: self._remove_download(d)
                )

            self.table.setCellWidget(row, 4, action_btn)

        # Update status label
        total = len(downloads)
        if total == 0:
            self.status_label.setText("No downloads")
        else:
            completed = sum(1 for d in downloads if d.status == DownloadStatus.COMPLETED)
            self.status_label.setText(
                f"{active_count} active, {completed} completed, {total} total"
            )

    def _on_download_started(self, download_id: int, total_size: int) -> None:
        """Handle download started."""
        if download_id in self._progress_widgets:
            self._progress_widgets[download_id].set_progress(0)

    def _on_download_progress(
        self, download_id: int, progress: float,
        downloaded: int, total: int, speed: float, eta: int
    ) -> None:
        """Handle download progress update."""
        if download_id in self._progress_widgets:
            self._progress_widgets[download_id].set_progress(
                progress, downloaded, total, speed, eta
            )

    def _on_download_completed(self, download_id: int, file_path: str) -> None:
        """Handle download completed."""
        if download_id in self._progress_widgets:
            self._progress_widgets[download_id].set_status(DownloadStatus.COMPLETED)
        self.refresh()

    def _on_download_failed(self, download_id: int, error: str) -> None:
        """Handle download failed."""
        if download_id in self._progress_widgets:
            self._progress_widgets[download_id].set_status(DownloadStatus.FAILED)
        self.refresh()

    def _cancel_download(self, download: Download) -> None:
        """Cancel a download."""
        self.download_manager.remove_download(download.id)

    def _remove_download(self, download: Download) -> None:
        """Remove a download from the list."""
        self.download_manager.remove_download(download.id)

    def _clear_completed(self) -> None:
        """Clear completed downloads."""
        self.download_manager.clear_completed()

    def _clear_all(self) -> None:
        """Clear all downloads (except active)."""
        downloads = self.download_manager.get_queue()
        for download in downloads:
            if not download.is_active:
                self.download_manager.remove_download(download.id)
