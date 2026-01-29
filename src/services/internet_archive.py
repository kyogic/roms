"""Internet Archive API client for the ROMs Downloader."""

import re
import time
import requests
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import quote

from ..utils.constants import SYSTEMS, REGIONS


class InternetArchiveClient:
    """Client for interacting with Internet Archive API."""

    BASE_URL = "https://archive.org"
    SEARCH_URL = f"{BASE_URL}/advancedsearch.php"
    METADATA_URL = f"{BASE_URL}/metadata"
    DOWNLOAD_URL = f"{BASE_URL}/download"

    def __init__(self, rate_limit: float = 1.0):
        """Initialize the Internet Archive client.

        Args:
            rate_limit: Minimum seconds between requests.
        """
        self.rate_limit = rate_limit
        self._last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ROMs-Downloader/1.0 (Educational purposes)"
        })

    def _throttle(self) -> None:
        """Throttle requests to respect rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a throttled request to the API.

        Args:
            url: URL to request.
            params: Query parameters.

        Returns:
            JSON response or None on error.
        """
        self._throttle()
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None

    def search_collection(
        self,
        collection: str,
        query: str = "",
        rows: int = 100,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Search for items in an Internet Archive collection.

        Args:
            collection: The IA collection identifier.
            query: Optional search query.
            rows: Number of results per page.
            page: Page number (1-indexed).

        Returns:
            List of item metadata dictionaries.
        """
        search_query = f"collection:{collection}"
        if query:
            search_query += f" AND ({query})"

        params = {
            "q": search_query,
            "output": "json",
            "rows": rows,
            "page": page,
            "fl[]": ["identifier", "title", "description", "creator", "date", "subject"]
        }

        data = self._make_request(self.SEARCH_URL, params)
        if data and "response" in data:
            return data["response"].get("docs", [])
        return []

    def get_item_metadata(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific item.

        Args:
            identifier: The IA item identifier.

        Returns:
            Item metadata dictionary or None.
        """
        url = f"{self.METADATA_URL}/{identifier}"
        return self._make_request(url)

    def get_item_files(self, identifier: str) -> List[Dict[str, Any]]:
        """Get the list of files in an item.

        Args:
            identifier: The IA item identifier.

        Returns:
            List of file metadata dictionaries.
        """
        metadata = self.get_item_metadata(identifier)
        if metadata and "files" in metadata:
            return metadata["files"]
        return []

    def get_download_url(self, identifier: str, filename: str) -> str:
        """Get the download URL for a file.

        Args:
            identifier: The IA item identifier.
            filename: The filename to download.

        Returns:
            Download URL string.
        """
        return f"{self.DOWNLOAD_URL}/{identifier}/{quote(filename)}"

    def search_roms_for_system(
        self,
        system_id: str,
        search_term: str = "",
        rows: int = 100,
        page: int = 1,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """Search for ROMs for a specific gaming system.

        Args:
            system_id: The system identifier (e.g., 'nes', 'snes').
            search_term: Optional search term to filter results.
            rows: Number of results per page.
            page: Page number.
            progress_callback: Callback for progress updates (current, total).

        Returns:
            List of game dictionaries.
        """
        if system_id not in SYSTEMS:
            return []

        system = SYSTEMS[system_id]
        all_games = []

        for i, collection in enumerate(system.ia_collections):
            items = self.search_collection(collection, search_term, rows, page)

            for item in items:
                games = self._process_item_for_system(item, system_id, system.file_extensions)
                all_games.extend(games)

            if progress_callback:
                progress_callback(i + 1, len(system.ia_collections))

        return all_games

    def _process_item_for_system(
        self,
        item: Dict[str, Any],
        system_id: str,
        extensions: List[str]
    ) -> List[Dict[str, Any]]:
        """Process an IA item and extract ROM information.

        Args:
            item: IA item metadata.
            system_id: Target system ID.
            extensions: Valid file extensions for this system.

        Returns:
            List of game dictionaries.
        """
        identifier = item.get("identifier", "")
        if not identifier:
            return []

        # Get detailed file list
        files = self.get_item_files(identifier)
        games = []

        for file_info in files:
            filename = file_info.get("name", "")
            if not filename:
                continue

            # Check if file has valid extension
            ext_match = any(filename.lower().endswith(ext) for ext in extensions)
            # Also check for compressed files
            is_archive = filename.lower().endswith(('.zip', '.7z', '.rar'))

            if not ext_match and not is_archive:
                continue

            # Parse game info from filename
            game_data = self._parse_game_from_filename(filename, identifier, system_id)
            game_data["file_size"] = int(file_info.get("size", 0))
            game_data["file_hash"] = file_info.get("md5", "")
            game_data["download_url"] = self.get_download_url(identifier, filename)

            # Add metadata from item
            if "description" in item:
                desc = item["description"]
                if isinstance(desc, list):
                    desc = " ".join(desc)
                game_data["description"] = desc[:500] if desc else ""

            if "creator" in item:
                creator = item["creator"]
                if isinstance(creator, list):
                    creator = creator[0]
                game_data["publisher"] = creator

            games.append(game_data)

        return games

    def _parse_game_from_filename(
        self,
        filename: str,
        identifier: str,
        system_id: str
    ) -> Dict[str, Any]:
        """Parse game information from a ROM filename.

        Args:
            filename: The ROM filename.
            identifier: IA item identifier.
            system_id: System ID.

        Returns:
            Dictionary with parsed game data.
        """
        # Remove extension
        name = filename
        for ext in ['.zip', '.7z', '.rar', '.nes', '.sfc', '.smc', '.n64', '.z64',
                    '.gb', '.gbc', '.gba', '.nds', '.iso', '.bin', '.cue', '.chd',
                    '.md', '.gen', '.sms', '.gg', '.pce', '.ngp', '.a26', '.a52',
                    '.a78', '.j64', '.jag', '.lnx', '.gdi', '.cdi']:
            if name.lower().endswith(ext):
                name = name[:-len(ext)]
                break

        # Parse region from filename
        region = "Unknown"
        region_patterns = [
            (r'\(USA\)', 'USA'),
            (r'\(U\)', 'USA'),
            (r'\(US\)', 'USA'),
            (r'\(Europe\)', 'Europe'),
            (r'\(E\)', 'Europe'),
            (r'\(EU\)', 'Europe'),
            (r'\(Japan\)', 'Japan'),
            (r'\(J\)', 'Japan'),
            (r'\(JP\)', 'Japan'),
            (r'\(World\)', 'World'),
            (r'\(W\)', 'World'),
            (r'\(PAL\)', 'PAL'),
        ]

        for pattern, reg in region_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                region = reg
                break

        # Clean up title - remove region tags, version info, etc.
        title = name
        # Remove parenthetical info
        title = re.sub(r'\s*\([^)]*\)\s*', ' ', title)
        # Remove brackets info
        title = re.sub(r'\s*\[[^\]]*\]\s*', ' ', title)
        # Clean up whitespace
        title = ' '.join(title.split())

        # Try to extract year
        year_match = re.search(r'\((\d{4})\)', name)
        release_year = int(year_match.group(1)) if year_match else None

        return {
            "ia_identifier": identifier,
            "title": title or filename,
            "system_id": system_id,
            "genre": "",
            "game_type": "",
            "publisher": "",
            "developer": "",
            "release_year": release_year,
            "region": region,
            "description": "",
            "file_name": filename,
        }

    def download_file(
        self,
        url: str,
        dest_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """Download a file with progress tracking.

        Args:
            url: URL to download.
            dest_path: Destination file path.
            progress_callback: Callback for progress updates (downloaded, total).

        Returns:
            True if successful, False otherwise.
        """
        try:
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)

            return True
        except (requests.RequestException, IOError) as e:
            print(f"Download error: {e}")
            return False
