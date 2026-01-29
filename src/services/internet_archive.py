"""Internet Archive API client for the ROMs Downloader."""

import re
import time
import requests
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import quote

from ..utils.constants import SYSTEMS, MULTI_SYSTEM_COLLECTIONS, SYSTEM_SEARCH_KEYWORDS


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
            "User-Agent": "ROMs-Downloader/1.0 (Educational/Preservation purposes; Python)"
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
            print(f"[IA] Requesting: {url}")
            if params:
                print(f"[IA] Query: {params.get('q', 'N/A')[:100]}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[IA] Request error: {e}")
            return None

    def search(
        self,
        query: str,
        rows: int = 100,
        page: int = 1,
        fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform a general search on Internet Archive.

        Args:
            query: Search query string.
            rows: Number of results per page.
            page: Page number (1-indexed).
            fields: List of fields to return.

        Returns:
            List of item metadata dictionaries.
        """
        if fields is None:
            fields = ["identifier", "title", "description", "creator", "date", "subject", "collection"]

        # Build URL manually to handle multiple fl[] parameters
        field_params = "&".join([f"fl[]={f}" for f in fields])
        full_url = f"{self.SEARCH_URL}?q={quote(query)}&output=json&rows={rows}&page={page}&{field_params}"

        data = self._make_request(full_url)
        if data and "response" in data:
            docs = data["response"].get("docs", [])
            total = data["response"].get("numFound", 0)
            print(f"[IA] Found {total} total results, returning {len(docs)}")
            return docs
        return []

    def search_collection(
        self,
        collection: str,
        title_search: str = "",
        rows: int = 100,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Search for items in an Internet Archive collection.

        Args:
            collection: The IA collection identifier.
            title_search: Optional title search term.
            rows: Number of results per page.
            page: Page number (1-indexed).

        Returns:
            List of item metadata dictionaries.
        """
        query = f"collection:{collection}"
        if title_search:
            # Search in title
            query += f" AND title:({title_search})"

        return self.search(query, rows, page)

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
        rows: int = 50,
        page: int = 1,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """Search for ROMs for a specific gaming system.

        Uses multiple search strategies:
        1. Search in known collections for the system
        2. Search by system keywords in title

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
            print(f"[IA] Unknown system: {system_id}")
            return []

        system = SYSTEMS[system_id]
        all_games = []
        seen_identifiers = set()

        # Calculate total steps
        total_collections = len(system.ia_collections)
        total_steps = total_collections + 1  # +1 for keyword search

        # Strategy 1: Search in system-specific collections
        for i, collection in enumerate(system.ia_collections):
            if progress_callback:
                progress_callback(i + 1, total_steps)

            print(f"[IA] Searching collection: {collection}")
            items = self.search_collection(collection, search_term, rows=rows, page=page)

            for item in items:
                identifier = item.get("identifier", "")
                if identifier and identifier not in seen_identifiers:
                    seen_identifiers.add(identifier)
                    games = self._process_item_for_system(item, system_id, system.file_extensions)
                    all_games.extend(games)

            # Stop early if we found enough results
            if len(all_games) >= rows * 2:
                break

        # Strategy 2: Search by system keywords in title (if we haven't found much)
        if len(all_games) < rows:
            if progress_callback:
                progress_callback(total_steps, total_steps)

            keywords = SYSTEM_SEARCH_KEYWORDS.get(system_id, [system.name])
            for keyword in keywords[:1]:  # Use first keyword only
                keyword_query = f'mediatype:software AND title:"{keyword}"'
                if search_term:
                    keyword_query += f' AND title:"{search_term}"'

                print(f"[IA] Keyword search: {keyword}")
                items = self.search(keyword_query, rows=rows, page=page)

                for item in items:
                    identifier = item.get("identifier", "")
                    if identifier and identifier not in seen_identifiers:
                        seen_identifiers.add(identifier)
                        games = self._process_item_for_system(item, system_id, system.file_extensions)
                        all_games.extend(games)

        print(f"[IA] Total games found for {system_id}: {len(all_games)}")
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
        if not files:
            print(f"[IA] No files found in {identifier}, using item metadata")
            # Create entry from item metadata alone
            game_data = self._create_game_from_item(item, identifier, system_id)
            return [game_data] if game_data else []

        games = []
        for file_info in files:
            filename = file_info.get("name", "")
            if not filename:
                continue

            # Check if file has valid extension
            ext_lower = filename.lower()
            ext_match = any(ext_lower.endswith(ext) for ext in extensions)
            # Also check for compressed files
            is_archive = ext_lower.endswith(('.zip', '.7z', '.rar'))

            if not ext_match and not is_archive:
                continue

            # Skip metadata/system files
            skip_exts = ('.xml', '.txt', '.sqlite', '.torrent', '.jpg', '.png', '.gif', '.nfo')
            if ext_lower.endswith(skip_exts):
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

    def _create_game_from_item(
        self,
        item: Dict[str, Any],
        identifier: str,
        system_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create a game entry from item metadata when file list unavailable.

        Args:
            item: IA item metadata.
            identifier: IA identifier.
            system_id: System ID.

        Returns:
            Game dictionary or None.
        """
        title = item.get("title", identifier)
        if not title:
            return None

        desc = item.get("description", "")
        if isinstance(desc, list):
            desc = " ".join(desc)

        return {
            "ia_identifier": identifier,
            "title": title,
            "system_id": system_id,
            "genre": "",
            "game_type": "",
            "publisher": item.get("creator", "") if isinstance(item.get("creator"), str) else "",
            "developer": "",
            "release_year": None,
            "region": "Unknown",
            "description": desc[:500] if desc else "",
            "file_name": "",
            "file_size": 0,
            "file_hash": "",
            "download_url": f"{self.DOWNLOAD_URL}/{identifier}",
        }

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
                    '.v64', '.gb', '.gbc', '.gba', '.nds', '.iso', '.bin', '.cue',
                    '.chd', '.md', '.gen', '.smd', '.sms', '.gg', '.pce', '.ngp',
                    '.a26', '.a52', '.a78', '.j64', '.jag', '.lnx', '.gdi', '.cdi',
                    '.gcm', '.gcz', '.rvz', '.img']:
            if name.lower().endswith(ext):
                name = name[:-len(ext)]
                break

        # Parse region from filename
        region = "Unknown"
        region_patterns = [
            (r'\(USA\)', 'USA'),
            (r'\(U\)', 'USA'),
            (r'\(US\)', 'USA'),
            (r'\(America\)', 'USA'),
            (r'\(Europe\)', 'Europe'),
            (r'\(E\)', 'Europe'),
            (r'\(EU\)', 'Europe'),
            (r'\(EUR\)', 'Europe'),
            (r'\(Japan\)', 'Japan'),
            (r'\(J\)', 'Japan'),
            (r'\(JP\)', 'Japan'),
            (r'\(JPN\)', 'Japan'),
            (r'\(World\)', 'World'),
            (r'\(W\)', 'World'),
            (r'\(PAL\)', 'PAL'),
            (r'\(NTSC\)', 'USA'),
        ]

        for pattern, reg in region_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                region = reg
                break

        # Clean up title
        title = name
        title = re.sub(r'\s*\([^)]*\)\s*', ' ', title)
        title = re.sub(r'\s*\[[^\]]*\]\s*', ' ', title)
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
            print(f"[IA] Downloading: {url}")
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

            print(f"[IA] Download complete: {dest_path}")
            return True
        except (requests.RequestException, IOError) as e:
            print(f"[IA] Download error: {e}")
            return False

    def test_connection(self) -> bool:
        """Test connection to Internet Archive.

        Returns:
            True if connection successful.
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/metadata/principalofshadows",
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
