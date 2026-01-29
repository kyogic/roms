"""Main entry point for the ROMs Downloader application."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from .ui import MainWindow
from .utils import ConfigManager, APP_NAME
from .database import DatabaseManager
from .services import DownloadManager


def main():
    """Main entry point for the application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("ROMs Downloader")

    # Get application directory
    app_dir = Path(__file__).parent.parent

    # Initialize managers
    config_manager = ConfigManager(app_dir)
    db_manager = DatabaseManager(app_dir / "roms_library.db")
    download_manager = DownloadManager(db_manager, config_manager)

    # Start download manager
    download_manager.start()

    # Create and show main window
    window = MainWindow(config_manager, db_manager, download_manager)
    window.show()

    # Run application
    result = app.exec()

    # Cleanup
    download_manager.stop()

    return result


if __name__ == "__main__":
    sys.exit(main())
