"""File organizer for the ROMs Downloader."""

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from ..utils.constants import SYSTEMS
from ..utils.config import ConfigManager


class FileOrganizer:
    """Organizes downloaded ROM files into a structured folder hierarchy."""

    def __init__(self, config_manager: ConfigManager):
        """Initialize the file organizer.

        Args:
            config_manager: Configuration manager instance.
        """
        self.config = config_manager
        self._temp_dir: Optional[Path] = None

    def get_download_path(self) -> Path:
        """Get the root download path."""
        path = self.config.get_download_path()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_system_path(self, system_id: str) -> Path:
        """Get the folder path for a specific system.

        Args:
            system_id: System identifier.

        Returns:
            Path to the system folder.
        """
        base_path = self.get_download_path()

        # Get system name for folder
        if system_id in SYSTEMS:
            folder_name = SYSTEMS[system_id].abbreviation
        else:
            folder_name = system_id.upper()

        system_path = base_path / folder_name
        system_path.mkdir(parents=True, exist_ok=True)
        return system_path

    def get_temp_dir(self) -> Path:
        """Get a temporary directory for downloads."""
        if self._temp_dir is None or not self._temp_dir.exists():
            self._temp_dir = Path(tempfile.mkdtemp(prefix="roms_download_"))
        return self._temp_dir

    def cleanup_temp_dir(self) -> None:
        """Clean up the temporary directory."""
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            self._temp_dir = None

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename to be safe for all filesystems.

        Args:
            filename: Original filename.

        Returns:
            Sanitized filename.
        """
        # Remove or replace invalid characters
        # Windows forbidden: < > : " / \ | ? *
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)

        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')

        # Limit length (Windows MAX_PATH consideration)
        max_length = 200
        if len(sanitized) > max_length:
            # Keep extension
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:max_length - len(ext)] + ext

        return sanitized

    def generate_filename(
        self,
        title: str,
        region: str,
        extension: str
    ) -> str:
        """Generate a standardized filename.

        Args:
            title: Game title.
            region: Region code.
            extension: File extension (with dot).

        Returns:
            Standardized filename.
        """
        # Use naming convention from config
        convention = self.config.get("namingConvention", "{title} ({region})")

        filename = convention.format(title=title, region=region)
        filename = self.sanitize_filename(filename)

        # Ensure extension
        if not filename.lower().endswith(extension.lower()):
            filename += extension

        return filename

    def organize_file(
        self,
        source_path: Path,
        system_id: str,
        title: str,
        region: str
    ) -> Path:
        """Organize a downloaded file into the proper location.

        Args:
            source_path: Path to the downloaded file.
            system_id: Target system ID.
            title: Game title.
            region: Region code.

        Returns:
            Path to the organized file.
        """
        # Get destination folder
        dest_folder = self.get_system_path(system_id)

        # Get original extension
        extension = source_path.suffix

        # Handle archives if auto-extract is enabled
        if self._is_archive(source_path):
            if self.config.get("autoExtract", True):
                extracted_path = self._extract_archive(source_path, system_id)
                if extracted_path:
                    extension = extracted_path.suffix
                    source_path = extracted_path

                    # Delete archive if not keeping
                    if not self.config.get("keepArchives", False):
                        archive_path = source_path.parent / (source_path.stem + ".zip")
                        if archive_path.exists():
                            archive_path.unlink()

        # Generate final filename
        filename = self.generate_filename(title, region, extension)
        dest_path = dest_folder / filename

        # Handle duplicates
        dest_path = self._handle_duplicate(dest_path)

        # Move or copy file
        shutil.move(str(source_path), str(dest_path))

        return dest_path

    def _is_archive(self, path: Path) -> bool:
        """Check if a file is an archive."""
        return path.suffix.lower() in ['.zip', '.7z', '.rar']

    def _extract_archive(
        self,
        archive_path: Path,
        system_id: str
    ) -> Optional[Path]:
        """Extract an archive and return the path to the ROM file.

        Args:
            archive_path: Path to the archive.
            system_id: System ID for file extension detection.

        Returns:
            Path to extracted ROM file, or None if extraction failed.
        """
        extract_dir = archive_path.parent / archive_path.stem
        extract_dir.mkdir(exist_ok=True)

        try:
            if archive_path.suffix.lower() == '.zip':
                import zipfile
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(extract_dir)

            elif archive_path.suffix.lower() == '.7z':
                import py7zr
                with py7zr.SevenZipFile(archive_path, 'r') as sz:
                    sz.extractall(extract_dir)

            elif archive_path.suffix.lower() == '.rar':
                import rarfile
                with rarfile.RarFile(archive_path, 'r') as rf:
                    rf.extractall(extract_dir)

            # Find the ROM file in extracted contents
            valid_extensions = []
            if system_id in SYSTEMS:
                valid_extensions = SYSTEMS[system_id].file_extensions

            for file in extract_dir.rglob('*'):
                if file.is_file():
                    if any(file.suffix.lower() == ext for ext in valid_extensions):
                        return file
                    # If no valid extensions found, return first non-trivial file
                    if file.stat().st_size > 1024:  # > 1KB
                        return file

        except Exception as e:
            print(f"Extraction error: {e}")

        return None

    def _handle_duplicate(self, path: Path) -> Path:
        """Handle duplicate filenames by adding a number suffix.

        Args:
            path: Desired file path.

        Returns:
            Path with unique filename.
        """
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1

        while True:
            new_path = parent / f"{stem} ({counter}){suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    def get_library_stats(self) -> dict:
        """Get statistics about the ROM library.

        Returns:
            Dictionary with library statistics.
        """
        base_path = self.get_download_path()
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_system": {}
        }

        if not base_path.exists():
            return stats

        for system_folder in base_path.iterdir():
            if system_folder.is_dir():
                system_files = list(system_folder.glob('*'))
                file_count = len([f for f in system_files if f.is_file()])
                total_size = sum(
                    f.stat().st_size for f in system_files if f.is_file()
                )

                stats["by_system"][system_folder.name] = {
                    "files": file_count,
                    "size": total_size
                }
                stats["total_files"] += file_count
                stats["total_size"] += total_size

        return stats
