"""Recommended emulators dialog for the ROMs Downloader."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt

from ..utils import SYSTEMS, SYSTEMS_BY_MANUFACTURER, RECOMMENDED_EMULATORS


class EmulatorsDialog(QDialog):
    """Dialog showing recommended emulators for each system."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Recommended Emulators")
        self.setMinimumSize(500, 500)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the emulators dialog UI."""
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            "Below are recommended emulators for each supported system.\n"
            "This is for informational purposes only - emulators are not integrated with this app."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Tree widget
        tree = QTreeWidget()
        tree.setHeaderLabels(["System / Emulator"])
        tree.setColumnCount(1)

        # Populate tree
        for manufacturer, system_ids in SYSTEMS_BY_MANUFACTURER.items():
            manufacturer_item = QTreeWidgetItem([manufacturer])
            manufacturer_item.setExpanded(True)

            for system_id in system_ids:
                if system_id not in SYSTEMS:
                    continue

                system = SYSTEMS[system_id]
                system_item = QTreeWidgetItem([f"{system.name} ({system.abbreviation})"])

                # Add emulators
                emulators = RECOMMENDED_EMULATORS.get(system_id, [])
                for emulator in emulators:
                    emulator_item = QTreeWidgetItem([emulator])
                    system_item.addChild(emulator_item)

                if not emulators:
                    no_emu_item = QTreeWidgetItem(["(No recommendations)"])
                    no_emu_item.setDisabled(True)
                    system_item.addChild(no_emu_item)

                manufacturer_item.addChild(system_item)

            tree.addTopLevelItem(manufacturer_item)

        # Add multi-system emulator note
        multi_item = QTreeWidgetItem(["Multi-System"])
        multi_item.setExpanded(True)
        retroarch_item = QTreeWidgetItem(["RetroArch"])
        retroarch_item.setToolTip(0, "Supports all systems through libretro cores")
        multi_note = QTreeWidgetItem(["(Supports all systems via libretro cores)"])
        multi_note.setDisabled(True)
        retroarch_item.addChild(multi_note)
        multi_item.addChild(retroarch_item)
        tree.addTopLevelItem(multi_item)

        tree.expandAll()
        layout.addWidget(tree)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
