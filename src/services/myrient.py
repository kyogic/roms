"""Myrient client for the ROMs Downloader."""

import re
import time
import requests
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import quote, unquote, urljoin


class MyrientDirectoryParser(HTMLParser):
    """Parse Myrient directory listings to extract file links."""

    def __init__(self):
        super().__init__()
        self.files = []
        self._in_link = False
        self._current_href = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value and not value.startswith("?") and not value.startswith("/"):
                    # Skip parent directory link
                    if value != "../":
                        self._current_href = value
                        self._in_link = True

    def handle_endtag(self, tag):
        if tag == "a":
            self._in_link = False
            self._current_href = ""

    def handle_data(self, data):
        if self._in_link and self._current_href:
            # Store the file info
            self.files.append({
                "href": self._current_href,
                "name": unquote(self._current_href.rstrip("/"))
            })
            self._current_href = ""


# Myrient collection paths for each system
# Using No-Intro for cartridge-based systems, Redump for disc-based
MYRIENT_SYSTEM_PATHS = {
    # Nintendo Systems
    "nes": "No-Intro/Nintendo - Nintendo Entertainment System (Headered)",
    "snes": "No-Intro/Nintendo - Super Nintendo Entertainment System",
    "n64": "No-Intro/Nintendo - Nintendo 64 (BigEndian)",
    "gcn": "Redump/Nintendo - GameCube - NKit RVZ [zstd-19-128k]",
    "gb": "No-Intro/Nintendo - Game Boy",
    "gbc": "No-Intro/Nintendo - Game Boy Color",
    "gba": "No-Intro/Nintendo - Game Boy Advance",
    "nds": "No-Intro/Nintendo - Nintendo DS (Decrypted)",

    # PlayStation Systems
    "ps1": "Redump/Sony - PlayStation",
    "ps2": "Redump/Sony - PlayStation 2",

    # Sega Systems
    "sms": "No-Intro/Sega - Master System - Mark III",
    "genesis": "No-Intro/Sega - Mega Drive - Genesis",
    "segacd": "Redump/Sega - Mega CD - Sega CD",
    "32x": "No-Intro/Sega - 32X",
    "saturn": "Redump/Sega - Saturn",
    "dreamcast": "Redump/Sega - Dreamcast",
    "gamegear": "No-Intro/Sega - Game Gear",

    # Atari Systems
    "atari2600": "No-Intro/Atari - 2600",
    "atari5200": "No-Intro/Atari - 5200",
    "atari7800": "No-Intro/Atari - 7800",
    "jaguar": "No-Intro/Atari - Jaguar",
    "lynx": "No-Intro/Atari - Lynx",

    # Other Systems
    "tg16": "No-Intro/NEC - PC Engine - TurboGrafx-16",
    "tgcd": "Redump/NEC - PC Engine CD - TurboGrafx-CD",
    "neogeo": "No-Intro/SNK - Neo Geo Pocket",  # Note: AES/MVS are in MAME
    "ngp": "No-Intro/SNK - Neo Geo Pocket Color",
    "3do": "Redump/3DO Interactive Multiplayer",
}

# Alternative/fallback collection paths for each system
# These are tried if the primary path fails
MYRIENT_ALTERNATIVE_PATHS = {
    # Nintendo - some have headerless versions or different formats
    "nes": [
        "No-Intro/Nintendo - Nintendo Entertainment System (Headerless)",
        "No-Intro/Nintendo - Family Computer Disk System",
    ],
    "snes": [
        "No-Intro/Nintendo - Satellaview",
        "No-Intro/Nintendo - Sufami Turbo",
    ],
    "n64": [
        "No-Intro/Nintendo - Nintendo 64 (ByteSwapped)",
        "No-Intro/Nintendo - Nintendo 64DD",
    ],
    "gcn": [
        "Redump/Nintendo - GameCube",
    ],
    "nds": [
        "No-Intro/Nintendo - Nintendo DS",
        "No-Intro/Nintendo - Nintendo DSi (Decrypted)",
    ],

    # PlayStation - CHD versions available
    "ps1": [
        "Redump/Sony - PlayStation - Datfile",
    ],
    "ps2": [
        "Redump/Sony - PlayStation 2 - Datfile",
    ],

    # Sega alternatives
    "genesis": [
        "No-Intro/Sega - Mega Drive - Genesis (Sega Channel)",
    ],
    "saturn": [
        "Redump/Sega - Saturn - Datfile",
    ],
    "dreamcast": [
        "Redump/Sega - Dreamcast - Datfile",
    ],

    # NEC alternatives
    "tg16": [
        "No-Intro/NEC - PC Engine SuperGrafx",
    ],
    "tgcd": [
        "Redump/NEC - PC Engine CD - TurboGrafx-CD - Datfile",
    ],
}


class MyrientClient:
    """Client for interacting with Myrient ROM archive."""

    BASE_URL = "https://myrient.erista.me/files"

    def __init__(self, rate_limit: float = 0.5):
        """Initialize the Myrient client.

        Args:
            rate_limit: Minimum seconds between requests.
        """
        self.rate_limit = rate_limit
        self._last_request_time = 0
        self.session = requests.Session()
        # Use browser-like headers to avoid being blocked
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def _throttle(self) -> None:
        """Throttle requests to respect rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, url: str) -> Optional[str]:
        """Make a throttled request.

        Args:
            url: URL to request.

        Returns:
            Response text or None on error.
        """
        self._throttle()
        try:
            print(f"[Myrient] Requesting: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[Myrient] Request error: {e}")
            return None

    def get_directory_listing(self, path: str) -> List[Dict[str, str]]:
        """Get a directory listing from Myrient.

        Args:
            path: Path relative to the base URL.

        Returns:
            List of file dictionaries with 'href' and 'name' keys.
        """
        url = f"{self.BASE_URL}/{quote(path, safe='/')}/"
        html = self._make_request(url)

        if not html:
            return []

        parser = MyrientDirectoryParser()
        parser.feed(html)
        return parser.files

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
            rows: Number of results to return.
            page: Page number (1-indexed).
            progress_callback: Callback for progress updates (current, total).

        Returns:
            List of game dictionaries.
        """
        if system_id not in MYRIENT_SYSTEM_PATHS:
            print(f"[Myrient] Unknown system: {system_id}")
            return []

        path = MYRIENT_SYSTEM_PATHS[system_id]

        if progress_callback:
            progress_callback(1, 3)

        print(f"[Myrient] Fetching directory: {path}")
        files = self.get_directory_listing(path)

        if progress_callback:
            progress_callback(2, 3)

        if not files:
            print(f"[Myrient] No files found at {path}")
            return []

        print(f"[Myrient] Found {len(files)} files in directory")

        # Filter to ROM files (usually .zip)
        rom_files = []
        for f in files:
            name = f["name"]
            # Skip non-ROM files
            if name.endswith(('.txt', '.xml', '.dat', '.html', '.htm')):
                continue
            rom_files.append(f)

        # Apply search filter
        if search_term:
            search_lower = search_term.lower()
            rom_files = [f for f in rom_files if search_lower in f["name"].lower()]

        print(f"[Myrient] {len(rom_files)} ROMs match filters")

        # Paginate
        start_idx = (page - 1) * rows
        end_idx = start_idx + rows
        page_files = rom_files[start_idx:end_idx]

        # Convert to game dictionaries
        games = []
        for f in page_files:
            game = self._parse_game_from_filename(f["name"], path, system_id)
            game["download_url"] = f"{self.BASE_URL}/{quote(path, safe='/')}/{quote(f['href'], safe='')}"
            games.append(game)

        if progress_callback:
            progress_callback(3, 3)

        print(f"[Myrient] Returning {len(games)} games for page {page}")
        return games

    def _parse_game_from_filename(
        self,
        filename: str,
        path: str,
        system_id: str
    ) -> Dict[str, Any]:
        """Parse game information from a ROM filename.

        Args:
            filename: The ROM filename.
            path: The Myrient collection path.
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

        # Parse region from filename (No-Intro format)
        region = "Unknown"
        region_patterns = [
            (r'\(USA\)', 'USA'),
            (r'\(USA,\s*Europe\)', 'USA'),
            (r'\(World\)', 'World'),
            (r'\(Europe\)', 'Europe'),
            (r'\(Japan\)', 'Japan'),
            (r'\(Japan,\s*USA\)', 'Japan'),
            (r'\(Japan,\s*Europe\)', 'Japan'),
            (r'\(Korea\)', 'Other'),
            (r'\(Australia\)', 'PAL'),
            (r'\(Brazil\)', 'Other'),
            (r'\(France\)', 'Europe'),
            (r'\(Germany\)', 'Europe'),
            (r'\(Spain\)', 'Europe'),
            (r'\(Italy\)', 'Europe'),
        ]

        for pattern, reg in region_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                region = reg
                break

        # Clean up title - remove tags in parentheses and brackets
        title = name
        title = re.sub(r'\s*\([^)]*\)\s*', ' ', title)
        title = re.sub(r'\s*\[[^\]]*\]\s*', ' ', title)
        title = ' '.join(title.split()).strip()

        # Try to extract year from original filename
        year_match = re.search(r'\((\d{4})\)', name)
        release_year = int(year_match.group(1)) if year_match else None

        return {
            "myrient_path": path,
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
            "file_size": 0,  # We don't get size from directory listing
            "file_hash": "",
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
            print(f"[Myrient] Downloading: {url}")

            # Add referer header to look more like a browser click
            headers = {
                "Referer": self.BASE_URL + "/",
                "Accept": "application/octet-stream,*/*",
            }

            response = self.session.get(
                url,
                stream=True,
                timeout=120,
                headers=headers,
                allow_redirects=True
            )

            # Log response details for debugging
            print(f"[Myrient] Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"[Myrient] Response headers: {dict(response.headers)}")

            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            print(f"[Myrient] File size: {total_size} bytes")

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)

            print(f"[Myrient] Download complete: {dest_path} ({downloaded} bytes)")
            return True
        except requests.RequestException as e:
            print(f"[Myrient] Download error: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[Myrient] Response status: {e.response.status_code}")
                print(f"[Myrient] Response text: {e.response.text[:500] if e.response.text else 'empty'}")
            return False
        except IOError as e:
            print(f"[Myrient] File I/O error: {e}")
            return False

    def test_connection(self) -> bool:
        """Test connection to Myrient.

        Returns:
            True if connection successful.
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/",
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_download_url(self, system_id: str, filename: str) -> str:
        """Get the download URL for a file.

        Args:
            system_id: The system ID.
            filename: The filename to download.

        Returns:
            Download URL string.
        """
        if system_id not in MYRIENT_SYSTEM_PATHS:
            return ""
        path = MYRIENT_SYSTEM_PATHS[system_id]
        return f"{self.BASE_URL}/{quote(path, safe='/')}/{quote(filename, safe='')}"

    def find_alternative_downloads(
        self,
        system_id: str,
        original_filename: str,
        original_url: str = ""
    ) -> List[Dict[str, Any]]:
        """Find alternative download sources for a ROM.

        Searches alternative collections and similar filenames to find
        the same game from different sources.

        Args:
            system_id: The system ID.
            original_filename: The original ROM filename.
            original_url: The original URL that failed (to avoid returning it).

        Returns:
            List of alternative game dictionaries with download_url.
        """
        alternatives = []

        # Extract the base game title for searching
        # Remove extension and version/region tags to get core title
        search_title = original_filename
        for ext in ['.zip', '.7z', '.rar', '.chd']:
            if search_title.lower().endswith(ext):
                search_title = search_title[:-len(ext)]
                break

        # Get first part before region/version tags
        # e.g., "Super Mario Bros. (USA) (Rev 1)" -> "Super Mario Bros"
        title_match = re.match(r'^([^([\]]+)', search_title)
        if title_match:
            search_title = title_match.group(1).strip()

        print(f"[Myrient] Searching alternatives for: {search_title}")

        # 1. Search in alternative collection paths
        alt_paths = MYRIENT_ALTERNATIVE_PATHS.get(system_id, [])
        for alt_path in alt_paths:
            print(f"[Myrient] Checking alternative path: {alt_path}")
            files = self.get_directory_listing(alt_path)

            for f in files:
                filename = f["name"]
                if search_title.lower() in filename.lower():
                    url = f"{self.BASE_URL}/{quote(alt_path, safe='/')}/{quote(f['href'], safe='')}"
                    if url != original_url:
                        game = self._parse_game_from_filename(filename, alt_path, system_id)
                        game["download_url"] = url
                        game["source"] = "alternative_collection"
                        alternatives.append(game)
                        print(f"[Myrient] Found alternative: {filename}")

        # 2. Search in primary collection for similar files (different regions/versions)
        primary_path = MYRIENT_SYSTEM_PATHS.get(system_id)
        if primary_path:
            print(f"[Myrient] Checking primary path for variants: {primary_path}")
            files = self.get_directory_listing(primary_path)

            for f in files:
                filename = f["name"]
                url = f"{self.BASE_URL}/{quote(primary_path, safe='/')}/{quote(f['href'], safe='')}"

                # Skip the original URL
                if url == original_url:
                    continue

                # Check if this is the same game (different region/version)
                if search_title.lower() in filename.lower():
                    game = self._parse_game_from_filename(filename, primary_path, system_id)
                    game["download_url"] = url
                    game["source"] = "variant"
                    alternatives.append(game)
                    print(f"[Myrient] Found variant: {filename}")

        print(f"[Myrient] Found {len(alternatives)} alternative downloads")
        return alternatives

    def download_with_fallback(
        self,
        url: str,
        dest_path: str,
        system_id: str,
        filename: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> tuple[bool, str]:
        """Download a file with automatic fallback to alternatives on failure.

        Args:
            url: Primary URL to download.
            dest_path: Destination file path.
            system_id: System ID for finding alternatives.
            filename: Original filename for finding alternatives.
            progress_callback: Callback for progress updates.

        Returns:
            Tuple of (success: bool, final_url: str).
        """
        # Try the primary URL first
        print(f"[Myrient] Attempting primary download: {url}")
        if self.download_file(url, dest_path, progress_callback):
            return True, url

        print(f"[Myrient] Primary download failed, searching for alternatives...")

        # Find alternatives
        alternatives = self.find_alternative_downloads(system_id, filename, url)

        # Try each alternative
        for alt in alternatives:
            alt_url = alt.get("download_url", "")
            if not alt_url:
                continue

            print(f"[Myrient] Trying alternative: {alt_url}")
            if self.download_file(alt_url, dest_path, progress_callback):
                print(f"[Myrient] Alternative download succeeded!")
                return True, alt_url

        print(f"[Myrient] All download attempts failed")
        return False, url
