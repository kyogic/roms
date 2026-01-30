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


# All supported gaming systems with VERIFIED Internet Archive collection identifiers
SYSTEMS: Dict[str, SystemInfo] = {
    # Nintendo Systems
    "nes": SystemInfo(
        id="nes",
        name="Nintendo Entertainment System",
        abbreviation="NES",
        manufacturer="Nintendo",
        generation="3rd",
        file_extensions=[".nes", ".unf", ".unif", ".zip"],
        ia_collections=[
            "nintendo-entertainment-system-all-nes-roms-goodnes",
            "classic-nintendo-roms-archive",
            "retro-roms-best-set",
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "snes": SystemInfo(
        id="snes",
        name="Super Nintendo Entertainment System",
        abbreviation="SNES",
        manufacturer="Nintendo",
        generation="4th",
        file_extensions=[".sfc", ".smc", ".zip"],
        ia_collections=[
            "snes-collection_202406",
            "CylesSNESRomPack",
            "classic-nintendo-roms-archive",
            "retro-roms-best-set",
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "n64": SystemInfo(
        id="n64",
        name="Nintendo 64",
        abbreviation="N64",
        manufacturer="Nintendo",
        generation="5th",
        file_extensions=[".n64", ".z64", ".v64", ".zip"],
        ia_collections=[
            "n64-collection",
            "N64-Roms-Col",
            "nintendo-64-rom-collection",
            "retro-roms-best-set",
            "N64TOSEC",
            "no-intro-rom-sets-2025",
        ]
    ),
    "gcn": SystemInfo(
        id="gcn",
        name="Nintendo GameCube",
        abbreviation="GCN",
        manufacturer="Nintendo",
        generation="6th",
        file_extensions=[".iso", ".gcm", ".gcz", ".rvz", ".zip"],
        ia_collections=[
            "nintendo-gamecube-roms",
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),
    "wii": SystemInfo(
        id="wii",
        name="Nintendo Wii",
        abbreviation="Wii",
        manufacturer="Nintendo",
        generation="7th",
        file_extensions=[".iso", ".wbfs", ".rvz", ".wia", ".zip"],
        ia_collections=[
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),
    "gb": SystemInfo(
        id="gb",
        name="Game Boy",
        abbreviation="GB",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".gb", ".zip"],
        ia_collections=[
            "classic-nintendo-roms-archive",
            "retro-roms-best-set",
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),
    "gbc": SystemInfo(
        id="gbc",
        name="Game Boy Color",
        abbreviation="GBC",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".gbc", ".zip"],
        ia_collections=[
            "classic-nintendo-roms-archive",
            "retro-roms-best-set",
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),
    "gba": SystemInfo(
        id="gba",
        name="Game Boy Advance",
        abbreviation="GBA",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".gba", ".zip"],
        ia_collections=[
            "classic-nintendo-roms-archive",
            "retro-roms-best-set",
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),
    "nds": SystemInfo(
        id="nds",
        name="Nintendo DS",
        abbreviation="NDS",
        manufacturer="Nintendo",
        generation="Handheld",
        file_extensions=[".nds", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),

    # PlayStation Systems
    "ps1": SystemInfo(
        id="ps1",
        name="PlayStation",
        abbreviation="PS1",
        manufacturer="Sony",
        generation="5th",
        file_extensions=[".bin", ".cue", ".iso", ".img", ".chd", ".zip"],
        ia_collections=[
            "ps1-collection_20240529",
            "2024-sony-playstation-usa-hearto-1g1r-collection",
            "sp1gcbcpt2",
            "retro-roms-best-set",
        ]
    ),
    "ps2": SystemInfo(
        id="ps2",
        name="PlayStation 2",
        abbreviation="PS2",
        manufacturer="Sony",
        generation="6th",
        file_extensions=[".iso", ".bin", ".chd", ".zip"],
        ia_collections=[
            "asurah94ps2_202405",
            "ps2usaredump1",
            "ps2usaredump1_20200816_1458",
            "sony_playstation2_g",
        ]
    ),

    # Sega Systems
    "sms": SystemInfo(
        id="sms",
        name="Sega Master System",
        abbreviation="SMS",
        manufacturer="Sega",
        generation="3rd",
        file_extensions=[".sms", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),
    "genesis": SystemInfo(
        id="genesis",
        name="Sega Genesis / Mega Drive",
        abbreviation="GEN",
        manufacturer="Sega",
        generation="4th",
        file_extensions=[".md", ".bin", ".gen", ".smd", ".zip"],
        ia_collections=[
            "mdplus_collection_22_04_16",
            "sega-genesis-romset-ultra-usa",
            "classic-nintendo-roms-archive",
            "retro-roms-best-set",
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "segacd": SystemInfo(
        id="segacd",
        name="Sega CD",
        abbreviation="SCD",
        manufacturer="Sega",
        generation="4th",
        file_extensions=[".bin", ".cue", ".iso", ".chd", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "32x": SystemInfo(
        id="32x",
        name="Sega 32X",
        abbreviation="32X",
        manufacturer="Sega",
        generation="4th",
        file_extensions=[".32x", ".bin", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "saturn": SystemInfo(
        id="saturn",
        name="Sega Saturn",
        abbreviation="SAT",
        manufacturer="Sega",
        generation="5th",
        file_extensions=[".bin", ".cue", ".iso", ".chd", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "dreamcast": SystemInfo(
        id="dreamcast",
        name="Sega Dreamcast",
        abbreviation="DC",
        manufacturer="Sega",
        generation="6th",
        file_extensions=[".gdi", ".cdi", ".chd", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "gamegear": SystemInfo(
        id="gamegear",
        name="Sega Game Gear",
        abbreviation="GG",
        manufacturer="Sega",
        generation="Handheld",
        file_extensions=[".gg", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
            "ultimate-rom-collection",
        ]
    ),

    # Atari Systems
    "atari2600": SystemInfo(
        id="atari2600",
        name="Atari 2600",
        abbreviation="2600",
        manufacturer="Atari",
        generation="2nd",
        file_extensions=[".a26", ".bin", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "atari5200": SystemInfo(
        id="atari5200",
        name="Atari 5200",
        abbreviation="5200",
        manufacturer="Atari",
        generation="2nd",
        file_extensions=[".a52", ".bin", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "atari7800": SystemInfo(
        id="atari7800",
        name="Atari 7800",
        abbreviation="7800",
        manufacturer="Atari",
        generation="3rd",
        file_extensions=[".a78", ".bin", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "jaguar": SystemInfo(
        id="jaguar",
        name="Atari Jaguar",
        abbreviation="JAG",
        manufacturer="Atari",
        generation="5th",
        file_extensions=[".j64", ".jag", ".bin", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "lynx": SystemInfo(
        id="lynx",
        name="Atari Lynx",
        abbreviation="LYNX",
        manufacturer="Atari",
        generation="Handheld",
        file_extensions=[".lnx", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),

    # Other Systems
    "tg16": SystemInfo(
        id="tg16",
        name="TurboGrafx-16 / PC Engine",
        abbreviation="TG16",
        manufacturer="NEC",
        generation="4th",
        file_extensions=[".pce", ".zip"],
        ia_collections=[
            "retro-roms-best-set",
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "tgcd": SystemInfo(
        id="tgcd",
        name="TurboGrafx-CD / PC Engine CD",
        abbreviation="TGCD",
        manufacturer="NEC",
        generation="4th",
        file_extensions=[".bin", ".cue", ".iso", ".chd", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "neogeo": SystemInfo(
        id="neogeo",
        name="Neo Geo",
        abbreviation="NEOGEO",
        manufacturer="SNK",
        generation="4th",
        file_extensions=[".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "ngp": SystemInfo(
        id="ngp",
        name="Neo Geo Pocket / Color",
        abbreviation="NGP",
        manufacturer="SNK",
        generation="Handheld",
        file_extensions=[".ngp", ".ngc", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
    "3do": SystemInfo(
        id="3do",
        name="3DO Interactive Multiplayer",
        abbreviation="3DO",
        manufacturer="3DO Company",
        generation="5th",
        file_extensions=[".iso", ".bin", ".cue", ".chd", ".zip"],
        ia_collections=[
            "hearto-1g1r-collection",
            "no-intro-rom-sets-2025",
        ]
    ),
}

# Multi-system ROM collections on Internet Archive (for broader searches)
MULTI_SYSTEM_COLLECTIONS = [
    "retro-roms-best-set",
    "hearto-1g1r-collection",
    "no-intro-rom-sets-2025",
    "ultimate-rom-collection",
    "classic-nintendo-roms-archive",
]

# Search keywords for each system (used when searching by title/description)
SYSTEM_SEARCH_KEYWORDS = {
    "nes": ["NES", "Nintendo Entertainment System", "Famicom"],
    "snes": ["SNES", "Super Nintendo", "Super Famicom"],
    "n64": ["N64", "Nintendo 64"],
    "gcn": ["GameCube", "GCN", "NGC"],
    "wii": ["Wii", "Nintendo Wii"],
    "gb": ["Game Boy", "Gameboy", "GB"],
    "gbc": ["Game Boy Color", "GBC"],
    "gba": ["Game Boy Advance", "GBA"],
    "nds": ["Nintendo DS", "NDS"],
    "ps1": ["PlayStation", "PSX", "PS1", "PSOne"],
    "ps2": ["PlayStation 2", "PS2"],
    "sms": ["Master System", "SMS", "Sega Master"],
    "genesis": ["Genesis", "Mega Drive", "Megadrive"],
    "segacd": ["Sega CD", "Mega CD"],
    "32x": ["32X", "Sega 32X"],
    "saturn": ["Saturn", "Sega Saturn"],
    "dreamcast": ["Dreamcast", "DC"],
    "gamegear": ["Game Gear", "Gamegear"],
    "atari2600": ["Atari 2600", "VCS"],
    "atari5200": ["Atari 5200"],
    "atari7800": ["Atari 7800"],
    "jaguar": ["Jaguar", "Atari Jaguar"],
    "lynx": ["Lynx", "Atari Lynx"],
    "tg16": ["TurboGrafx", "PC Engine", "TG16", "PCE"],
    "tgcd": ["TurboGrafx-CD", "PC Engine CD"],
    "neogeo": ["Neo Geo", "NeoGeo", "Neo-Geo"],
    "ngp": ["Neo Geo Pocket"],
    "3do": ["3DO"],
}

# Organize systems by manufacturer for UI
SYSTEMS_BY_MANUFACTURER = {
    "Nintendo": ["nes", "snes", "n64", "gcn", "wii", "gb", "gbc", "gba", "nds"],
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
    "wii": ["Dolphin"],
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
