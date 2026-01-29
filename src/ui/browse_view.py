"""Browse view for browsing and searching ROMs."""

from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QPushButton, QLabel, QHeaderView, QMessageBox,
    QProgressDialog, QAbstractItemView, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ..database import DatabaseManager
from ..services import DownloadManager, InternetArchiveClient
from ..utils import SYSTEMS, GENRES, REGIONS, GAMES_DATABASE


class SearchWorker(QThread):
    """Worker thread for searching Internet Archive."""

    finished = pyqtSignal(list)  # List of games found
    progress = pyqtSignal(int, int)  # current, total
    error = pyqtSignal(str)

    def __init__(self, system_id: str, search_term: str):
        super().__init__()
        self.system_id = system_id
        self.search_term = search_term
        self.ia_client = InternetArchiveClient()

    def run(self):
        try:
            games = self.ia_client.search_roms_for_system(
                self.system_id,
                self.search_term,
                rows=100,
                progress_callback=lambda c, t: self.progress.emit(c, t)
            )
            self.finished.emit(games)
        except Exception as e:
            self.error.emit(str(e))


class BrowseView(QWidget):
    """Widget for browsing and searching ROMs."""

    def __init__(self, db_manager: DatabaseManager, download_manager: DownloadManager):
        super().__init__()
        self.db = db_manager
        self.download_manager = download_manager

        self._current_system: Optional[str] = None
        self._current_games: List[Dict[str, Any]] = []
        self._search_worker: Optional[SearchWorker] = None

        self._setup_ui()
        self._connect_signals()

        # Auto-load pre-populated games if catalog is empty
        self._ensure_catalog_populated()

    def _setup_ui(self) -> None:
        """Set up the browse view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Search and filter bar
        filter_layout = QHBoxLayout()

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title...")
        self.search_input.setClearButtonEnabled(True)
        filter_layout.addWidget(self.search_input)

        # Genre filter
        filter_layout.addWidget(QLabel("Genre:"))
        self.genre_combo = QComboBox()
        self.genre_combo.addItem("All Genres", None)
        for genre in GENRES:
            self.genre_combo.addItem(genre, genre)
        self.genre_combo.setMinimumWidth(120)
        filter_layout.addWidget(self.genre_combo)

        # Region filter
        filter_layout.addWidget(QLabel("Region:"))
        self.region_combo = QComboBox()
        self.region_combo.addItem("All Regions", None)
        for region in REGIONS.keys():
            self.region_combo.addItem(region, region)
        self.region_combo.setMinimumWidth(100)
        filter_layout.addWidget(self.region_combo)

        # Search button
        self.search_btn = QPushButton("Search Online")
        self.search_btn.setToolTip("Search Internet Archive for ROMs")
        filter_layout.addWidget(self.search_btn)

        # Load sample games button
        self.load_samples_btn = QPushButton("Load Sample Games")
        self.load_samples_btn.setToolTip("Load a database of popular games to browse")
        filter_layout.addWidget(self.load_samples_btn)

        layout.addLayout(filter_layout)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Title", "System", "Genre", "Region", "Size", "Status"
        ])

        # Table settings
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 100)

        layout.addWidget(self.table)

        # Detail panel
        detail_group = QGroupBox("Game Details")
        detail_layout = QVBoxLayout(detail_group)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(100)
        detail_layout.addWidget(self.detail_text)

        # Download buttons
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.setEnabled(False)
        btn_layout.addWidget(self.download_btn)

        self.download_all_btn = QPushButton("Download All Regions")
        self.download_all_btn.setEnabled(False)
        btn_layout.addWidget(self.download_all_btn)

        btn_layout.addStretch()

        self.result_label = QLabel("Select a system to browse ROMs")
        btn_layout.addWidget(self.result_label)

        detail_layout.addLayout(btn_layout)

        layout.addWidget(detail_group)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self.search_input.returnPressed.connect(self._filter_results)
        self.search_input.textChanged.connect(self._filter_results)
        self.genre_combo.currentIndexChanged.connect(self._filter_results)
        self.region_combo.currentIndexChanged.connect(self._filter_results)
        self.search_btn.clicked.connect(self._search_online)
        self.load_samples_btn.clicked.connect(self._load_sample_games)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._on_double_click)

        self.download_btn.clicked.connect(self._download_selected)
        self.download_all_btn.clicked.connect(self._download_all_regions)

    def _ensure_catalog_populated(self) -> None:
        """Ensure the catalog has games, auto-load samples if empty."""
        if self.db.is_catalog_empty():
            count = self.db.load_prepopulated_games(GAMES_DATABASE)
            if count > 0:
                print(f"[Browse] Auto-loaded {count} sample games into catalog")

    def _load_sample_games(self) -> None:
        """Load sample games into the catalog."""
        count = self.db.load_prepopulated_games(GAMES_DATABASE)
        if count > 0:
            QMessageBox.information(
                self,
                "Games Loaded",
                f"Loaded {count} sample games into the catalog.\n\n"
                "These are popular titles for each system. "
                "Use 'Search Online' to find more games from Internet Archive."
            )
            self._load_games_from_db()
        else:
            QMessageBox.information(
                self,
                "Already Loaded",
                "Sample games are already in your catalog."
            )

    def set_system_filter(self, system_id: Optional[str]) -> None:
        """Set the current system filter.

        Args:
            system_id: System ID to filter by, or None for all.
        """
        self._current_system = system_id

        if system_id:
            system = SYSTEMS.get(system_id)
            system_name = system.name if system else system_id
            self.result_label.setText(f"Browsing: {system_name}")
        else:
            self.result_label.setText("Select a system to browse ROMs")

        self._load_games_from_db()

    def _load_games_from_db(self) -> None:
        """Load games from the local database."""
        search = self.search_input.text().strip() or None
        genre = self.genre_combo.currentData()
        region = self.region_combo.currentData()

        games = self.db.get_games(
            system_id=self._current_system,
            genre=genre,
            region=region,
            search=search,
            order_by="title",
            limit=1000
        )

        self._current_games = games
        self._populate_table(games)

    def _filter_results(self) -> None:
        """Filter the current results based on search/filter inputs."""
        self._load_games_from_db()

    def _search_online(self) -> None:
        """Search Internet Archive for ROMs."""
        if not self._current_system:
            QMessageBox.warning(
                self,
                "Select System",
                "Please select a system from the sidebar first."
            )
            return

        search_term = self.search_input.text().strip()

        # Create and show progress dialog
        self.progress_dialog = QProgressDialog(
            f"Searching Internet Archive for {SYSTEMS[self._current_system].name} ROMs...",
            "Cancel",
            0, 100,
            self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.show()

        # Start search worker
        self._search_worker = SearchWorker(self._current_system, search_term)
        self._search_worker.progress.connect(self._on_search_progress)
        self._search_worker.finished.connect(self._on_search_finished)
        self._search_worker.error.connect(self._on_search_error)
        self._search_worker.start()

    def _on_search_progress(self, current: int, total: int) -> None:
        """Handle search progress update."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_dialog.setValue(progress)

    def _on_search_finished(self, games: List[Dict[str, Any]]) -> None:
        """Handle search completion."""
        self.progress_dialog.close()

        # Save games to database
        for game in games:
            self.db.add_game(game)

        # Reload from database
        self._load_games_from_db()

        QMessageBox.information(
            self,
            "Search Complete",
            f"Found {len(games)} ROMs from Internet Archive.\n"
            "Results have been saved to your local catalog."
        )

    def _on_search_error(self, error: str) -> None:
        """Handle search error."""
        self.progress_dialog.close()
        QMessageBox.critical(
            self,
            "Search Error",
            f"An error occurred while searching:\n{error}"
        )

    def _populate_table(self, games: List[Dict[str, Any]]) -> None:
        """Populate the table with games."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(games))

        for row, game in enumerate(games):
            # Title
            title_item = QTableWidgetItem(game.get("title", ""))
            title_item.setData(Qt.ItemDataRole.UserRole, game)
            self.table.setItem(row, 0, title_item)

            # System
            system_id = game.get("system_id", "")
            system = SYSTEMS.get(system_id)
            system_abbr = system.abbreviation if system else system_id.upper()
            self.table.setItem(row, 1, QTableWidgetItem(system_abbr))

            # Genre
            self.table.setItem(row, 2, QTableWidgetItem(game.get("genre", "")))

            # Region
            self.table.setItem(row, 3, QTableWidgetItem(game.get("region", "")))

            # Size
            size = game.get("file_size", 0)
            size_str = self._format_size(size)
            self.table.setItem(row, 4, QTableWidgetItem(size_str))

            # Status
            game_id = game.get("id", 0)
            download_url = game.get("download_url", "")
            if self.db.is_in_library(game_id):
                status = "Downloaded"
            elif download_url:
                status = "Available"
            else:
                status = "Search to DL"  # Need to search IA to get download URL
            self.table.setItem(row, 5, QTableWidgetItem(status))

        self.table.setSortingEnabled(True)
        self.result_label.setText(f"Showing {len(games)} ROMs")

    def _format_size(self, size: int) -> str:
        """Format file size to human readable."""
        if size == 0:
            return "Unknown"

        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _on_selection_changed(self) -> None:
        """Handle table selection change."""
        selected = self.table.selectedItems()
        if selected:
            game = selected[0].data(Qt.ItemDataRole.UserRole)
            self._show_game_details(game)
            self.download_btn.setEnabled(True)
            self.download_all_btn.setEnabled(True)
        else:
            self.detail_text.clear()
            self.download_btn.setEnabled(False)
            self.download_all_btn.setEnabled(False)

    def _show_game_details(self, game: Dict[str, Any]) -> None:
        """Show details for a game in the detail panel."""
        details = []
        details.append(f"<b>{game.get('title', 'Unknown')}</b>")

        if game.get("publisher"):
            details.append(f"Publisher: {game['publisher']}")
        if game.get("developer"):
            details.append(f"Developer: {game['developer']}")
        if game.get("release_year"):
            details.append(f"Year: {game['release_year']}")
        if game.get("description"):
            desc = game["description"][:200]
            if len(game["description"]) > 200:
                desc += "..."
            details.append(f"<br>{desc}")

        self.detail_text.setHtml("<br>".join(details))

    def _on_double_click(self) -> None:
        """Handle double-click on a row."""
        self._download_selected()

    def _download_selected(self) -> None:
        """Download the selected ROM."""
        selected = self.table.selectedItems()
        if not selected:
            return

        game = selected[0].data(Qt.ItemDataRole.UserRole)
        game_id = game.get("id")
        download_url = game.get("download_url", "")

        if not game_id:
            QMessageBox.warning(
                self,
                "Cannot Download",
                "This game doesn't have valid download information."
            )
            return

        # Check if we have a download URL
        if not download_url:
            result = QMessageBox.question(
                self,
                "Search Required",
                f"'{game.get('title', 'ROM')}' needs to be searched on Internet Archive first.\n\n"
                "Would you like to search for it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                self.search_input.setText(game.get("title", ""))
                self._search_online()
            return

        if self.db.is_in_library(game_id):
            result = QMessageBox.question(
                self,
                "Already Downloaded",
                "This ROM is already in your library. Download again?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes:
                return

        # Add to download queue
        self.download_manager.add_download(game_id)
        QMessageBox.information(
            self,
            "Download Added",
            f"'{game.get('title', 'ROM')}' has been added to the download queue."
        )

    def _download_all_regions(self) -> None:
        """Download all region variants of the selected game."""
        selected = self.table.selectedItems()
        if not selected:
            return

        game = selected[0].data(Qt.ItemDataRole.UserRole)
        title = game.get("title", "")

        # Find all games with the same title
        all_games = self.db.get_games(
            system_id=game.get("system_id"),
            search=title,
            limit=100
        )

        # Filter to exact title matches
        matching_games = [g for g in all_games if g.get("title") == title]

        if len(matching_games) <= 1:
            QMessageBox.information(
                self,
                "No Other Regions",
                "No other region variants found for this game."
            )
            return

        result = QMessageBox.question(
            self,
            "Download All Regions",
            f"Found {len(matching_games)} region variants.\nDownload all?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            for g in matching_games:
                if g.get("id") and not self.db.is_in_library(g["id"]):
                    self.download_manager.add_download(g["id"])

            QMessageBox.information(
                self,
                "Downloads Added",
                f"Added {len(matching_games)} ROMs to the download queue."
            )

    def refresh(self) -> None:
        """Refresh the view."""
        self._load_games_from_db()
