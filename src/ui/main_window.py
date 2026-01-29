"""Main window for the ROMs Downloader application."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction

from .browse_view import BrowseView
from .downloads_view import DownloadsView
from .settings_dialog import SettingsDialog
from .disclaimer_dialog import DisclaimerDialog
from .emulators_dialog import EmulatorsDialog
from ..utils import (
    APP_NAME, APP_VERSION, SYSTEMS, SYSTEMS_BY_MANUFACTURER,
    ConfigManager, RECOMMENDED_EMULATORS
)
from ..database import DatabaseManager
from ..services import DownloadManager


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(
        self,
        config_manager: ConfigManager,
        db_manager: DatabaseManager,
        download_manager: DownloadManager
    ):
        super().__init__()
        self.config = config_manager
        self.db = db_manager
        self.download_manager = download_manager

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._connect_signals()

        # Check if disclaimer has been accepted
        if not self.config.is_disclaimer_accepted():
            self._show_disclaimer()

    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(QSize(1000, 700))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter for sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left sidebar - System tree
        self.system_tree = QTreeWidget()
        self.system_tree.setHeaderLabel("Systems")
        self.system_tree.setMinimumWidth(180)
        self.system_tree.setMaximumWidth(250)
        self._populate_system_tree()
        splitter.addWidget(self.system_tree)

        # Right side - Tab widget
        self.tabs = QTabWidget()

        # Browse tab
        self.browse_view = BrowseView(self.db, self.download_manager)
        self.tabs.addTab(self.browse_view, "Browse")

        # Downloads tab
        self.downloads_view = DownloadsView(self.download_manager)
        self.tabs.addTab(self.downloads_view, "Downloads")

        splitter.addWidget(self.tabs)

        # Set splitter sizes
        splitter.setSizes([200, 800])

        main_layout.addWidget(splitter)

    def _populate_system_tree(self) -> None:
        """Populate the system tree widget."""
        # Add "All Systems" item
        all_item = QTreeWidgetItem(["All Systems"])
        all_item.setData(0, Qt.ItemDataRole.UserRole, None)
        self.system_tree.addTopLevelItem(all_item)

        # Add systems by manufacturer
        for manufacturer, system_ids in SYSTEMS_BY_MANUFACTURER.items():
            manufacturer_item = QTreeWidgetItem([manufacturer])
            manufacturer_item.setData(0, Qt.ItemDataRole.UserRole, None)

            for system_id in system_ids:
                if system_id in SYSTEMS:
                    system = SYSTEMS[system_id]
                    system_item = QTreeWidgetItem([system.abbreviation])
                    system_item.setData(0, Qt.ItemDataRole.UserRole, system_id)
                    system_item.setToolTip(0, system.name)
                    manufacturer_item.addChild(system_item)

            self.system_tree.addTopLevelItem(manufacturer_item)

        # Expand all by default
        self.system_tree.expandAll()

    def _setup_menu(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_view)
        view_menu.addAction(refresh_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        emulators_action = QAction("Recommended &Emulators", self)
        emulators_action.triggered.connect(self._show_emulators)
        tools_menu.addAction(emulators_action)

        clear_completed_action = QAction("&Clear Completed Downloads", self)
        clear_completed_action.triggered.connect(self._clear_completed)
        tools_menu.addAction(clear_completed_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        legal_action = QAction("&Legal Disclaimer", self)
        legal_action.triggered.connect(self._show_disclaimer)
        help_menu.addAction(legal_action)

        help_menu.addSeparator()

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self) -> None:
        """Set up the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Add permanent widgets
        self.library_label = QLabel("Library: 0 ROMs")
        self.statusbar.addPermanentWidget(self.library_label)

        self._update_library_count()

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # System tree selection
        self.system_tree.itemClicked.connect(self._on_system_selected)

        # Download manager signals
        self.download_manager.download_completed.connect(self._on_download_completed)
        self.download_manager.queue_updated.connect(self._update_download_count)

    def _on_system_selected(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle system selection in the tree."""
        system_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.browse_view.set_system_filter(system_id)

    def _on_download_completed(self, download_id: int, file_path: str) -> None:
        """Handle download completion."""
        self._update_library_count()
        self.statusbar.showMessage(f"Download completed: {file_path}", 5000)

    def _update_library_count(self) -> None:
        """Update the library count in the status bar."""
        count = len(self.db.get_library())
        self.library_label.setText(f"Library: {count} ROMs")

    def _update_download_count(self) -> None:
        """Update the downloads tab title with pending count."""
        pending = [d for d in self.download_manager.get_queue()
                   if d.is_active]
        count = len(pending)
        if count > 0:
            self.tabs.setTabText(1, f"Downloads ({count})")
        else:
            self.tabs.setTabText(1, "Downloads")

    def _show_settings(self) -> None:
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            self.statusbar.showMessage("Settings saved", 3000)

    def _show_emulators(self) -> None:
        """Show the recommended emulators dialog."""
        dialog = EmulatorsDialog(self)
        dialog.exec()

    def _show_disclaimer(self) -> None:
        """Show the legal disclaimer dialog."""
        dialog = DisclaimerDialog(self.config, self)
        result = dialog.exec()

        # If user didn't accept and hasn't accepted before, close app
        if not result and not self.config.is_disclaimer_accepted():
            QMessageBox.warning(
                self,
                "Disclaimer Required",
                "You must accept the legal disclaimer to use this application."
            )
            self.close()

    def _show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {APP_VERSION}</p>"
            "<p>A tool for browsing, downloading, and organizing ROMs from "
            "Internet Archive.</p>"
            "<p>For educational and preservation purposes only.</p>"
        )

    def _refresh_view(self) -> None:
        """Refresh the current view."""
        self.browse_view.refresh()
        self.downloads_view.refresh()

    def _clear_completed(self) -> None:
        """Clear completed downloads."""
        self.download_manager.clear_completed()
        self.downloads_view.refresh()

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Stop download manager
        self.download_manager.stop()

        # Save config
        self.config.save()

        event.accept()
