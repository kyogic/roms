"""Database manager for the ROMs Downloader."""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

from ..utils.constants import DATABASE_FILE, SYSTEMS


class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_path: Path = None):
        """Initialize the database manager.

        Args:
            db_path: Path to the database file. Defaults to app directory.
        """
        if db_path is None:
            app_dir = Path(__file__).parent.parent.parent
            db_path = app_dir / DATABASE_FILE

        self.db_path = Path(db_path)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database with schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r") as f:
            schema = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema)
            self._populate_systems(conn)

    def _populate_systems(self, conn: sqlite3.Connection) -> None:
        """Populate the systems table with known systems."""
        for system_id, system in SYSTEMS.items():
            conn.execute(
                """
                INSERT OR IGNORE INTO systems (id, name, abbreviation, manufacturer, generation)
                VALUES (?, ?, ?, ?, ?)
                """,
                (system.id, system.name, system.abbreviation, system.manufacturer, system.generation)
            )

    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # Game operations
    def add_game(self, game_data: Dict[str, Any]) -> int:
        """Add a game to the catalog.

        Args:
            game_data: Dictionary with game information.

        Returns:
            The ID of the inserted game.
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT OR REPLACE INTO games
                (ia_identifier, title, system_id, genre, game_type, publisher, developer,
                 release_year, region, description, file_size, file_name, file_hash, download_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    game_data.get("ia_identifier"),
                    game_data.get("title"),
                    game_data.get("system_id"),
                    game_data.get("genre"),
                    game_data.get("game_type"),
                    game_data.get("publisher"),
                    game_data.get("developer"),
                    game_data.get("release_year"),
                    game_data.get("region"),
                    game_data.get("description"),
                    game_data.get("file_size"),
                    game_data.get("file_name"),
                    game_data.get("file_hash"),
                    game_data.get("download_url"),
                )
            )
            return cursor.lastrowid

    def get_games(
        self,
        system_id: Optional[str] = None,
        genre: Optional[str] = None,
        region: Optional[str] = None,
        search: Optional[str] = None,
        order_by: str = "title",
        order_dir: str = "ASC",
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get games with optional filtering and sorting.

        Args:
            system_id: Filter by system.
            genre: Filter by genre.
            region: Filter by region.
            search: Search in title.
            order_by: Column to sort by.
            order_dir: Sort direction (ASC or DESC).
            limit: Maximum number of results.
            offset: Offset for pagination.

        Returns:
            List of game dictionaries.
        """
        query = "SELECT * FROM games WHERE 1=1"
        params: List[Any] = []

        if system_id:
            query += " AND system_id = ?"
            params.append(system_id)

        if genre:
            query += " AND genre = ?"
            params.append(genre)

        if region:
            query += " AND region = ?"
            params.append(region)

        if search:
            query += " AND title LIKE ?"
            params.append(f"%{search}%")

        # Validate order_by to prevent SQL injection
        valid_columns = ["title", "genre", "game_type", "release_year", "region", "file_size"]
        if order_by not in valid_columns:
            order_by = "title"

        order_dir = "DESC" if order_dir.upper() == "DESC" else "ASC"
        query += f" ORDER BY {order_by} {order_dir}"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_game_by_id(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Get a game by its ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_game_count(self, system_id: Optional[str] = None) -> int:
        """Get the count of games, optionally filtered by system."""
        query = "SELECT COUNT(*) FROM games"
        params: List[Any] = []

        if system_id:
            query += " WHERE system_id = ?"
            params.append(system_id)

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]

    # Library operations
    def add_to_library(self, game_id: int, file_path: str) -> int:
        """Add a downloaded ROM to the library."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT OR REPLACE INTO library (game_id, file_path)
                VALUES (?, ?)
                """,
                (game_id, file_path)
            )
            return cursor.lastrowid

    def get_library(
        self,
        system_id: Optional[str] = None,
        order_by: str = "downloaded_at",
        order_dir: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """Get the user's library with game info."""
        query = """
            SELECT l.*, g.title, g.system_id, g.genre, g.region, g.file_size
            FROM library l
            JOIN games g ON l.game_id = g.id
            WHERE 1=1
        """
        params: List[Any] = []

        if system_id:
            query += " AND g.system_id = ?"
            params.append(system_id)

        valid_columns = ["downloaded_at", "title", "system_id"]
        if order_by not in valid_columns:
            order_by = "downloaded_at"

        order_dir = "DESC" if order_dir.upper() == "DESC" else "ASC"
        query += f" ORDER BY {order_by} {order_dir}"

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def is_in_library(self, game_id: int) -> bool:
        """Check if a game is in the library."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM library WHERE game_id = ?",
                (game_id,)
            )
            return cursor.fetchone()[0] > 0

    # Download operations
    def add_download(self, game_id: int) -> int:
        """Add a game to the download queue."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO downloads (game_id, status) VALUES (?, 'pending')",
                (game_id,)
            )
            return cursor.lastrowid

    def update_download_status(
        self,
        download_id: int,
        status: str,
        progress: float = 0,
        error_message: Optional[str] = None
    ) -> None:
        """Update the status of a download."""
        with self.get_connection() as conn:
            if status == "downloading" and progress == 0:
                conn.execute(
                    """
                    UPDATE downloads
                    SET status = ?, progress = ?, started_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (status, progress, download_id)
                )
            elif status == "completed":
                conn.execute(
                    """
                    UPDATE downloads
                    SET status = ?, progress = 100, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (status, download_id)
                )
            elif status == "failed":
                conn.execute(
                    """
                    UPDATE downloads
                    SET status = ?, error_message = ?
                    WHERE id = ?
                    """,
                    (status, error_message, download_id)
                )
            else:
                conn.execute(
                    "UPDATE downloads SET status = ?, progress = ? WHERE id = ?",
                    (status, progress, download_id)
                )

    def get_pending_downloads(self) -> List[Dict[str, Any]]:
        """Get all pending downloads with game info."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT d.*, g.title, g.system_id, g.download_url, g.file_name
                FROM downloads d
                JOIN games g ON d.game_id = g.id
                WHERE d.status IN ('pending', 'downloading')
                ORDER BY d.id
                """
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_all_downloads(self) -> List[Dict[str, Any]]:
        """Get all downloads with game info."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT d.*, g.title, g.system_id, g.download_url, g.file_name
                FROM downloads d
                JOIN games g ON d.game_id = g.id
                ORDER BY d.id DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]

    def remove_download(self, download_id: int) -> None:
        """Remove a download from the queue."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM downloads WHERE id = ?", (download_id,))

    def clear_completed_downloads(self) -> None:
        """Clear all completed downloads from the queue."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM downloads WHERE status = 'completed'")
