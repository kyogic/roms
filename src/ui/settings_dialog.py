"""Settings dialog for the ROMs Downloader."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QSpinBox, QCheckBox,
    QFileDialog, QDialogButtonBox, QGroupBox, QLabel,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt

from ..utils import ConfigManager, REGIONS


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager

        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setModal(True)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up the settings dialog UI."""
        layout = QVBoxLayout(self)

        # Download settings group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)

        # Download path
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(browse_btn)

        download_layout.addRow("Download Folder:", path_layout)

        # Concurrent downloads
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 5)
        self.concurrent_spin.setToolTip("Number of simultaneous downloads")
        download_layout.addRow("Concurrent Downloads:", self.concurrent_spin)

        # Speed limit
        speed_layout = QHBoxLayout()
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(0, 100000)
        self.speed_spin.setSuffix(" KB/s")
        self.speed_spin.setSpecialValueText("Unlimited")
        self.speed_spin.setToolTip("0 = Unlimited")
        speed_layout.addWidget(self.speed_spin)
        speed_layout.addStretch()
        download_layout.addRow("Speed Limit:", speed_layout)

        layout.addWidget(download_group)

        # File handling group
        file_group = QGroupBox("File Handling")
        file_layout = QVBoxLayout(file_group)

        self.auto_extract_check = QCheckBox("Automatically extract compressed files")
        file_layout.addWidget(self.auto_extract_check)

        self.keep_archives_check = QCheckBox("Keep original archive files after extraction")
        file_layout.addWidget(self.keep_archives_check)

        layout.addWidget(file_group)

        # Region priority group
        region_group = QGroupBox("Region Priority")
        region_layout = QVBoxLayout(region_group)

        region_layout.addWidget(QLabel(
            "Drag to reorder. Higher items have higher priority when downloading."
        ))

        self.region_list = QListWidget()
        self.region_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.region_list.setMaximumHeight(150)
        region_layout.addWidget(self.region_list)

        layout.addWidget(region_group)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_close)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def _load_settings(self) -> None:
        """Load current settings into the UI."""
        self.path_input.setText(str(self.config.get_download_path()))
        self.concurrent_spin.setValue(self.config.get("maxConcurrentDownloads", 2))
        self.speed_spin.setValue(self.config.get("speedLimitKbps", 0))
        self.auto_extract_check.setChecked(self.config.get("autoExtract", True))
        self.keep_archives_check.setChecked(self.config.get("keepArchives", False))

        # Load region priority
        self.region_list.clear()
        priority = self.config.get_region_priority()
        for region in priority:
            item = QListWidgetItem(region)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
            self.region_list.addItem(item)

        # Add any missing regions
        for region in REGIONS.keys():
            if region not in priority:
                item = QListWidgetItem(region)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
                self.region_list.addItem(item)

    def _browse_folder(self) -> None:
        """Open folder browser dialog."""
        current_path = self.path_input.text()
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            current_path
        )
        if folder:
            self.path_input.setText(folder)

    def _save_and_close(self) -> None:
        """Save settings and close the dialog."""
        self.config.set("downloadPath", self.path_input.text())
        self.config.set("maxConcurrentDownloads", self.concurrent_spin.value())
        self.config.set("speedLimitKbps", self.speed_spin.value())
        self.config.set("autoExtract", self.auto_extract_check.isChecked())
        self.config.set("keepArchives", self.keep_archives_check.isChecked())

        # Save region priority
        region_priority = []
        for i in range(self.region_list.count()):
            region_priority.append(self.region_list.item(i).text())
        self.config.set("regionPriority", region_priority)

        self.config.save()
        self.accept()
