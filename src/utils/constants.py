"""System constants and definitions for the ROMs Downloader."""

from dataclasses import dataclass
from typing import Dict, List

APP_NAME = "ROMs Downloader & Organizer"
APP_VERSION = "1.0.0"
CONFIG_FILE = "config.json"
DATABASE_FILE = "roms_library.db"


@dataclass
class SystemInfo:
    """Information about a gaming system."""
    id: str
    name: str
    abbreviation: str
    manufacturer: str
    generation: str
    file_extensions: List[str]
    ia_collections: List[str]


# All supported gaming systems
SYSTEMS: Dict[str, SystemInfo] = {
    # Nintendo Systems
    "nes": SystemInfo(
        id="nes",
        name="Nintendo Entertainment System",
        abbreviation="NES",
        manufacturer="Nintendo",
        generation="3rd",
        file_extensions=[".nes", ".unf", ".unif"],
        ia_collections=["nes-roms", "no-intro_nes"]
    ),
    "snes": SystemInfo(
        id="snes",
        name="Super Nintendo Entertainment System",
        abbreviation="SNES",
        manufacturer="Nintendo",
        generation="4th",
        file_extensions=[".sfc", ".smc"],
        ia_collections=["snes-roms", "no-intro_snes"]
    ),
    "n64": SystemInfo(
        id="n64",
        name="Nintendo 64",
        abbreviation="N64",
        manufacturer="Nintendo",
        generation="5th",
        file_extensions=[".n64", ".z64", ".v64"],
        ia_collections=["n64-roms", "no-intro_n64"]
    ),
    "gcn": SystemInfo(
        id="gcn",
        name="Nintendo GameCube",
        abbreviation="GCN",
        manufacturer="Nintendo",
        generation="6th",
        file_extensions=[".iso", ".gcm", ".gcz", ".rvz"],
        ia_collections=["gamecube-usa", "gamecube-collection"]
    ),
    "gb": SystemInfo(
        id="gb",
        name="Game Boy",
        abbreviation="GB",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".gb"],
        ia_collections=["no-intro_gameboy", "gameboy-roms"]
    ),
    "gbc": SystemInfo(
        id="gbc",
        name="Game Boy Color",
        abbreviation="GBC",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".gbc"],
        ia_collections=["no-intro_gbc", "gameboy-color-roms"]
    ),
    "gba": SystemInfo(
        id="gba",
        name="Game Boy Advance",
        abbreviation="GBA",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".gba"],
        ia_collections=["no-intro_gba", "gba-roms"]
    ),
    "nds": SystemInfo(
        id="nds",
        name="Nintendo DS",
        abbreviation="NDS",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".nds"],
        ia_collections=["no-intro_nds", "nds-roms"]
    ),

    # PlayStation Systems
    "ps1": SystemInfo(
        id="ps1",
        name="PlayStation",
        abbreviation="PS1",
        manufacturer="Sony",
        generation="5th",
        file_extensions=[".bin", ".cue", ".iso", ".img", ".chd"],
        ia_collections=["redump_psx", "psx-collection", "sony_playstation"]
    ),
    "ps2": SystemInfo(
        id="ps2",
        name="PlayStation 2",
        abbreviation="PS2",
        manufacturer="Sony",
        generation="6th",
        file_extensions=[".iso", ".bin", ".chd"],
        ia_collections=["redump_ps2", "ps2-collection"]
    ),

    # Sega Systems
    "sms": SystemInfo(
        id="sms",
        name="Sega Master System",
        abbreviation="SMS",
        manufacturer="Sega",
        generation="3rd",
        file_extensions=[".sms"],
        ia_collections=["no-intro_sms", "sega-master-system"]
    ),
    "genesis": SystemInfo(
        id="genesis",
        name="Sega Genesis / Mega Drive",
        abbreviation="GEN",
        manufacturer="Sega",
        generation="4th",
        file_extensions=[".md", ".bin", ".gen"],
        ia_collections=["no-intro_genesis", "genesis-roms", "sega-genesis"]
    ),
    "segacd": SystemInfo(
        id="segacd",
        name="Sega CD",
        abbreviation="SCD",
        manufacturer="Sega",
        generation="4th",
        file_extensions=[".bin", ".cue", ".iso", ".chd"],
        ia_collections=["sega-cd-usa", "redump_segacd"]
    ),
    "32x": SystemInfo(
        id="32x",
        name="Sega 32X",
        abbreviation="32X",
        manufacturer="Sega",
        generation="4th",
        file_extensions=[".32x", ".bin"],
        ia_collections=["no-intro_32x", "sega-32x"]
    ),
    "saturn": SystemInfo(
        id="saturn",
        name="Sega Saturn",
        abbreviation="SAT",
        manufacturer="Sega",
        generation="5th",
        file_extensions=[".bin", ".cue", ".iso", ".chd"],
        ia_collections=["redump_saturn", "sega-saturn"]
    ),
    "dreamcast": SystemInfo(
        id="dreamcast",
        name="Sega Dreamcast",
        abbreviation="DC",
        manufacturer="Sega",
        generation="6th",
        file_extensions=[".gdi", ".cdi", ".chd"],
        ia_collections=["redump_dreamcast", "dreamcast-collection"]
    ),
    "gamegear": SystemInfo(
        id="gamegear",
        name="Sega Game Gear",
        abbreviation="GG",
        manufacturer="Sega",
        generation="Handheld",
        file_extensions=[".gg"],
        ia_collections=["no-intro_gamegear", "game-gear-roms"]
    ),

    # Atari Systems
    "atari2600": SystemInfo(
        id="atari2600",
        name="Atari 2600",
        abbreviation="2600",
        manufacturer="Atari",
        generation="2nd",
        file_extensions=[".a26", ".bin"],
        ia_collections=["atari-2600-roms", "no-intro_atari2600"]
    ),
    "atari5200": SystemInfo(
        id="atari5200",
        name="Atari 5200",
        abbreviation="5200",
        manufacturer="Atari",
        generation="2nd",
        file_extensions=[".a52", ".bin"],
        ia_collections=["atari-5200-roms"]
    ),
    "atari7800": SystemInfo(
        id="atari7800",
        name="Atari 7800",
        abbreviation="7800",
        manufacturer="Atari",
        generation="3rd",
        file_extensions=[".a78", ".bin"],
        ia_collections=["atari-7800-roms", "no-intro_atari7800"]
    ),
    "jaguar": SystemInfo(
        id="jaguar",
        name="Atari Jaguar",
        abbreviation="JAG",
        manufacturer="Atari",
        generation="5th",
        file_extensions=[".j64", ".jag", ".bin"],
        ia_collections=["atari-jaguar-roms"]
    ),
    "lynx": SystemInfo(
        id="lynx",
        name="Atari Lynx",
        abbreviation="LYNX",
        manufacturer="Atari",
        generation="Handheld",
        file_extensions=[".lnx"],
        ia_collections=["no-intro_lynx", "atari-lynx-roms"]
    ),

    # Other Systems
    "tg16": SystemInfo(
        id="tg16",
        name="TurboGrafx-16 / PC Engine",
        abbreviation="TG16",
        manufacturer="NEC",
        generation="4th",
        file_extensions=[".pce"],
        ia_collections=["turbografx-16-roms", "no-intro_pce"]
    ),
    "tgcd": SystemInfo(
        id="tgcd",
        name="TurboGrafx-CD / PC Engine CD",
        abbreviation="TGCD",
        manufacturer="NEC",
        generation="4th",
        file_extensions=[".bin", ".cue", ".iso", ".chd"],
        ia_collections=["turbografx-cd-roms"]
    ),
    "neogeo": SystemInfo(
        id="neogeo",
        name="Neo Geo",
        abbreviation="NEOGEO",
        manufacturer="SNK",
        generation="4th",
        file_extensions=[".zip"],  # Neo Geo uses zip archives with multiple files
        ia_collections=["neo-geo-roms", "neogeo-collection"]
    ),
    "ngp": SystemInfo(
        id="ngp",
        name="Neo Geo Pocket / Color",
        abbreviation="NGP",
        manufacturer="SNK",
        generation="Handheld",
        file_extensions=[".ngp", ".ngc"],
        ia_collections=["no-intro_ngp", "neo-geo-pocket-roms"]
    ),
    "3do": SystemInfo(
        id="3do",
        name="3DO Interactive Multiplayer",
        abbreviation="3DO",
        manufacturer="3DO Company",
        generation="5th",
        file_extensions=[".iso", ".bin", ".cue", ".chd"],
        ia_collections=["3do-collection", "redump_3do"]
    ),
}

# Organize systems by manufacturer for UI
SYSTEMS_BY_MANUFACTURER = {
    "Nintendo": ["nes", "snes", "n64", "gcn", "gb", "gbc", "gba", "nds"],
    "Sony": ["ps1", "ps2"],
    "Sega": ["sms", "genesis", "segacd", "32x", "saturn", "dreamcast", "gamegear"],
    "Atari": ["atari2600", "atari5200", "atari7800", "jaguar", "lynx"],
    "Other": ["tg16", "tgcd", "neogeo", "ngp", "3do"],
}

# Game genres for categorization
GENRES = [
    "Action",
    "Action-Adventure",
    "Adventure",
    "Beat 'em Up",
    "Educational",
    "Fighting",
    "Horror",
    "Music/Rhythm",
    "Platformer",
    "Puzzle",
    "Racing",
    "RPG",
    "Shooter",
    "Simulation",
    "Sports",
    "Strategy",
    "Visual Novel",
    "Other",
]

# Region codes with priority
REGIONS = {
    "USA": 1,
    "Europe": 2,
    "Japan": 3,
    "World": 4,
    "PAL": 5,
    "Other": 6,
}

# Recommended emulators per system
RECOMMENDED_EMULATORS = {
    "nes": ["Mesen", "FCEUX", "Nestopia"],
    "snes": ["bsnes", "Snes9x", "ZSNES"],
    "n64": ["Project64", "Mupen64Plus", "simple64"],
    "gcn": ["Dolphin"],
    "gb": ["SameBoy", "BGB", "mGBA"],
    "gbc": ["SameBoy", "BGB", "mGBA"],
    "gba": ["mGBA", "VBA-M"],
    "nds": ["DeSmuME", "melonDS"],
    "ps1": ["DuckStation", "ePSXe", "Mednafen"],
    "ps2": ["PCSX2"],
    "sms": ["Emulicious", "Kega Fusion"],
    "genesis": ["Kega Fusion", "BlastEm", "Genesis Plus GX"],
    "segacd": ["Kega Fusion", "Genesis Plus GX"],
    "32x": ["Kega Fusion", "PicoDrive"],
    "saturn": ["Mednafen", "SSF", "Kronos"],
    "dreamcast": ["Flycast", "Redream"],
    "gamegear": ["Emulicious", "Kega Fusion"],
    "atari2600": ["Stella"],
    "atari5200": ["Atari800", "Altirra"],
    "atari7800": ["ProSystem", "A7800"],
    "jaguar": ["BigPEmu", "Virtual Jaguar"],
    "lynx": ["Mednafen", "Handy"],
    "tg16": ["Mednafen", "Ootake"],
    "tgcd": ["Mednafen", "Ootake"],
    "neogeo": ["FinalBurn Neo", "MAME"],
    "ngp": ["Mednafen", "NeoPop"],
    "3do": ["4DO", "Opera"],
}

# Default configuration
DEFAULT_CONFIG = {
    "downloadPath": "C:\\ROMs",
    "organizationScheme": "by-system",
    "namingConvention": "{title} ({region})",
    "regionPriority": ["USA", "Europe", "Japan", "World"],
    "autoExtract": True,
    "keepArchives": False,
    "maxConcurrentDownloads": 2,
    "speedLimitKbps": 0,
    "theme": "system",
    "disclaimerAccepted": False,
}
