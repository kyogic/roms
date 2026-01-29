# Product Requirements Document (PRD)
# ROMs Downloader and Organizer

## 1. Overview

### 1.1 Product Vision
A Windows desktop application built with Python that allows users to browse, download, and organize video game ROMs from Internet Archive. The app provides a comprehensive catalog of titles from classic gaming systems (up to 6th generation), with robust metadata management and organization features.

### 1.2 Target Users
- Retro gaming enthusiasts
- ROM collectors and archivists
- Emulator users who want organized game libraries

### 1.3 Key Value Propositions
- Centralized browsing of ROMs across multiple console generations
- One-click downloads from Internet Archive
- Automatic metadata fetching and organization
- Flexible sorting and categorization options
- Clean folder structure for emulator compatibility

---

## 2. Supported Systems

### 2.1 Nintendo Systems
| System | Abbreviation | Generation | Typical ROM Size |
|--------|--------------|------------|------------------|
| Nintendo Entertainment System | NES | 3rd | 8KB - 1MB |
| Super Nintendo Entertainment System | SNES | 4th | 512KB - 6MB |
| Nintendo 64 | N64 | 5th | 8MB - 64MB |
| GameCube | GCN | 6th | 1.4GB |
| Game Boy | GB | Handheld | 32KB - 1MB |
| Game Boy Color | GBC | Handheld | 32KB - 2MB |
| Game Boy Advance | GBA | Handheld | 1MB - 32MB |
| Nintendo DS | NDS | Handheld | 8MB - 512MB |

### 2.2 PlayStation Systems
| System | Abbreviation | Generation | Typical ROM Size |
|--------|--------------|------------|------------------|
| PlayStation | PS1/PSX | 5th | 300MB - 700MB |
| PlayStation 2 | PS2 | 6th | 1GB - 4.7GB |

### 2.3 Sega Systems
| System | Abbreviation | Generation | Typical ROM Size |
|--------|--------------|------------|------------------|
| Sega Master System | SMS | 3rd | 32KB - 512KB |
| Sega Genesis / Mega Drive | GEN/MD | 4th | 512KB - 4MB |
| Sega CD | SCD | 4th | 300MB - 700MB |
| Sega 32X | 32X | 4th | 1MB - 3MB |
| Sega Saturn | SAT | 5th | 300MB - 700MB |
| Sega Dreamcast | DC | 6th | 700MB - 1GB |
| Sega Game Gear | GG | Handheld | 32KB - 1MB |

### 2.4 Atari Systems
| System | Abbreviation | Generation | Typical ROM Size |
|--------|--------------|------------|------------------|
| Atari 2600 | 2600 | 2nd | 2KB - 32KB |
| Atari 5200 | 5200 | 2nd | 8KB - 32KB |
| Atari 7800 | 7800 | 3rd | 16KB - 128KB |
| Atari Jaguar | JAG | 5th | 1MB - 6MB |
| Atari Lynx | LYNX | Handheld | 128KB - 512KB |

### 2.5 Other Systems
| System | Abbreviation | Generation | Typical ROM Size |
|--------|--------------|------------|------------------|
| NEC TurboGrafx-16 / PC Engine | TG16/PCE | 4th | 256KB - 2.5MB |
| NEC TurboGrafx-CD / PC Engine CD | TGCD | 4th | 300MB - 700MB |
| SNK Neo Geo | NEOGEO | 4th | 50MB - 500MB |
| SNK Neo Geo Pocket / Color | NGP/NGPC | Handheld | 1MB - 4MB |
| 3DO Interactive Multiplayer | 3DO | 5th | 300MB - 700MB |

---

## 3. Core Features

### 3.1 Game Catalog Browser
- **Title List View**: Display all available titles per system
- **Search Functionality**: Search by title, genre, publisher, year
- **Filtering Options**: Filter by system, region, genre, game type
- **Sorting Options**:
  - Title (A-Z, Z-A)
  - Genre
  - Game Type (Action, RPG, Sports, etc.)
  - Release Year
  - Publisher
  - File Size
  - Region

### 3.2 Download Management
- **Source**: Internet Archive ROM collections
- **Queue System**: Add multiple ROMs to download queue
- **Progress Tracking**: Real-time download progress per item
- **Pause/Resume**: Ability to pause and resume downloads
- **Retry Logic**: Automatic retry on failed downloads
- **Multi-Region Support**: Download all available regions with USA priority

### 3.3 Folder Organization
- **Custom Download Location**: User-selectable root download folder via folder picker dialog
- **Folder Structure**: Organized by System
  ```
  C:\ROMs\
    ├── NES\
    │   ├── Super Mario Bros (USA).nes
    │   ├── Super Mario Bros (Europe).nes
    │   └── Super Mario Bros (Japan).nes
    ├── SNES\
    │   ├── Chrono Trigger (USA).sfc
    │   └── ...
    ├── Genesis\
    │   └── ...
    ├── PS1\
    │   └── ...
    └── ...
  ```
- **File Naming**: `{Title} ({Region}).{ext}` format
- **Duplicate Detection**: Warn when ROM already exists

### 3.4 Metadata Management
- **Auto-fetch Metadata**: Pull metadata from Internet Archive
- **Storage Format**: SQLite database (efficient for sorting/filtering large collections)
- **Stored Metadata Fields**:
  - Title
  - System/Platform
  - Genre
  - Game Type (2D Platformer, 3D Action, Turn-based RPG, etc.)
  - Publisher
  - Developer
  - Release Year
  - Region (USA, EUR, JPN, etc.)
  - Description
  - File Size
  - File Hash (for verification)
  - Download Date
  - Internet Archive Identifier
- **Manual Edit**: Allow users to edit/correct metadata

### 3.5 Library Management (Existing ROMs)
- **Import Existing**: Scan user's existing ROM folders
- **Auto-identify**: Attempt to identify ROMs by filename/hash
- **Organize Existing**: Move/rename existing ROMs to match organization scheme
- **Collection Stats**: Show library statistics (total games, per system, etc.)

---

## 4. User Interface

### 4.1 Technology Stack
- **Language**: Python 3.10+
- **GUI Framework**: PyQt6 (recommended) or Tkinter
- **Platform**: Windows (primary)
- **Database**: SQLite3
- **HTTP Client**: requests / aiohttp

### 4.2 Main Views
1. **Browse View**: List of available ROMs to download (per system)
2. **Library View**: User's downloaded/imported ROMs
3. **Downloads View**: Active and queued downloads
4. **Settings View**: App configuration

### 4.3 UI Components
- System selector sidebar (tree or list view)
- Search bar with filter dropdowns
- Game list table (sortable columns)
- Detail panel (full metadata, download button)
- Download queue panel with progress bars
- Status bar with connection/download status

### 4.4 UI Mockup
```
┌─────────────────────────────────────────────────────────────────────┐
│  ROMs Downloader & Organizer                            [─] [□] [×] │
├──────────────┬──────────────────────────────────────────────────────┤
│ Systems      │  Search: [_______________] [Genre ▼] [Region ▼]      │
│ ───────────  ├──────────────────────────────────────────────────────┤
│ ▸ Nintendo   │  Title              │ Genre    │ Year │ Region │ Size │
│   ├ NES      │ ─────────────────────────────────────────────────────│
│   ├ SNES     │  Super Mario Bros   │ Platform │ 1985 │ USA    │ 40KB │
│   ├ N64      │  Legend of Zelda    │ Action   │ 1986 │ USA    │ 128K │
│   ├ GameCube │  Metroid            │ Action   │ 1986 │ USA    │ 128K │
│   └ ...      │  Mega Man 2         │ Platform │ 1988 │ USA    │ 256K │
│ ▸ PlayStation│  ...                │          │      │        │      │
│ ▸ Sega       ├──────────────────────────────────────────────────────┤
│ ▸ Atari      │  Selected: Super Mario Bros (USA)                    │
│ ▸ Other      │  Publisher: Nintendo | Developer: Nintendo R&D4      │
│              │  Description: Classic platformer...                  │
│──────────────│                                                      │
│ Downloads (3)│  [Download USA] [Download All Regions]               │
│ ───────────  ├──────────────────────────────────────────────────────┤
│ Zelda   45%  │                                                      │
│ Mario   100% │                                                      │
│ Metroid Queue│                                                      │
├──────────────┴──────────────────────────────────────────────────────┤
│ Status: Connected to Internet Archive | Downloaded: 1,234 ROMs      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Architecture

### 5.1 Project Structure
```
roms-downloader/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── browse_view.py      # ROM browser widget
│   │   ├── library_view.py     # Library management widget
│   │   ├── downloads_view.py   # Download queue widget
│   │   └── settings_dialog.py  # Settings configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── internet_archive.py # IA API client
│   │   ├── download_manager.py # Download queue & progress
│   │   ├── metadata_service.py # Metadata fetching & storage
│   │   └── file_organizer.py   # File organization logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── game.py             # Game/ROM data model
│   │   ├── system.py           # Console system model
│   │   └── download.py         # Download task model
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py       # SQLite connection manager
│   │   └── schema.sql          # Database schema
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       └── constants.py        # System definitions, etc.
├── resources/
│   └── icons/                  # Application icons
├── tests/
│   └── ...
├── requirements.txt
├── config.json                 # User configuration
└── README.md
```

### 5.2 Database Schema
```sql
-- Systems table
CREATE TABLE systems (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    abbreviation TEXT NOT NULL,
    generation TEXT,
    manufacturer TEXT
);

-- Games catalog (from Internet Archive)
CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ia_identifier TEXT UNIQUE,
    title TEXT NOT NULL,
    system_id TEXT REFERENCES systems(id),
    genre TEXT,
    game_type TEXT,
    publisher TEXT,
    developer TEXT,
    release_year INTEGER,
    region TEXT,
    description TEXT,
    file_size INTEGER,
    file_hash TEXT,
    download_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User's library (downloaded ROMs)
CREATE TABLE library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER REFERENCES games(id),
    file_path TEXT NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE
);

-- Download queue
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER REFERENCES games(id),
    status TEXT DEFAULT 'pending',  -- pending, downloading, completed, failed
    progress REAL DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Indexes for fast sorting/filtering
CREATE INDEX idx_games_system ON games(system_id);
CREATE INDEX idx_games_genre ON games(genre);
CREATE INDEX idx_games_title ON games(title);
CREATE INDEX idx_games_region ON games(region);
```

### 5.3 Key Components
```
┌─────────────────────────────────────────────────────────────────┐
│                        UI Layer (PyQt6)                          │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│   │  Browse  │ │ Library  │ │Downloads │ │     Settings     │   │
│   │   View   │ │   View   │ │   View   │ │      Dialog      │   │
│   └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                       Service Layer                              │
│   ┌────────────────┐ ┌────────────────┐ ┌────────────────────┐  │
│   │    Internet    │ │    Download    │ │    File          │   │
│   │ Archive Client │ │    Manager     │ │    Organizer     │   │
│   └────────────────┘ └────────────────┘ └────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        Data Layer                                │
│   ┌────────────────┐ ┌────────────────┐ ┌────────────────────┐  │
│   │    SQLite      │ │   Config       │ │    File System     │  │
│   │   Database     │ │   Manager      │ │     Operations     │  │
│   └────────────────┘ └────────────────┘ └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Internet Archive Integration

### 6.1 API Endpoints
- **Search**: `https://archive.org/advancedsearch.php`
- **Metadata**: `https://archive.org/metadata/{identifier}`
- **Download**: `https://archive.org/download/{identifier}/{filename}`

### 6.2 Known ROM Collections
| System | Internet Archive Collection |
|--------|----------------------------|
| NES | `nes-roms`, `no-intro_nes` |
| SNES | `snes-roms`, `no-intro_snes` |
| N64 | `n64-roms`, `no-intro_n64` |
| GameCube | `gamecube-collection` |
| PS1 | `redump_psx`, `psx-collection` |
| PS2 | `redump_ps2`, `ps2-collection` |
| Genesis | `genesis-roms`, `no-intro_genesis` |
| Dreamcast | `dreamcast-collection` |
| Saturn | `saturn-collection` |
| And more... | (to be discovered via API) |

### 6.3 Download Process
1. User selects game from catalog
2. Fetch item metadata from IA
3. Get download URL(s) for all regions
4. Display region options (USA priority highlighted)
5. Add selected region(s) to download queue
6. Download with progress tracking
7. Verify file integrity (if hash available)
8. Extract if compressed (zip, 7z)
9. Rename to standard format: `{Title} ({Region}).{ext}`
10. Move to appropriate system folder
11. Store metadata in SQLite database

### 6.4 Rate Limiting
- Implement request throttling (1 request/second for metadata)
- Respect IA's robots.txt and rate limits
- Queue management for bulk downloads
- Configurable concurrent downloads (default: 2)

---

## 7. Configuration

### 7.1 Default Settings
```json
{
  "downloadPath": "C:\\ROMs",
  "organizationScheme": "by-system",
  "namingConvention": "{title} ({region})",
  "regionPriority": ["USA", "Europe", "Japan", "World"],
  "autoExtract": true,
  "keepArchives": false,
  "maxConcurrentDownloads": 2,
  "speedLimitKbps": 0,
  "theme": "system",
  "checkUpdatesOnStart": true
}
```

### 7.2 Configuration UI
- Download folder picker (Windows folder browser dialog)
- Region priority drag-and-drop list
- Concurrent downloads slider (1-5)
- Speed limit input (0 = unlimited)
- Auto-extract checkbox
- Keep archives checkbox

---

## 8. Recommended Emulators

The app will display recommended emulators for each system (information only, no integration).

| System | Recommended Emulators |
|--------|----------------------|
| NES | Mesen, FCEUX, Nestopia |
| SNES | bsnes, Snes9x, ZSNES |
| N64 | Project64, Mupen64Plus, simple64 |
| GameCube | Dolphin |
| Game Boy/GBC | SameBoy, BGB, mGBA |
| GBA | mGBA, VBA-M |
| NDS | DeSmuME, melonDS |
| PS1 | DuckStation, ePSXe, Mednafen |
| PS2 | PCSX2 |
| Genesis | Kega Fusion, BlastEm, Genesis Plus GX |
| Saturn | Mednafen, SSF, Kronos |
| Dreamcast | Flycast, Redream |
| Atari 2600 | Stella |
| Atari 7800 | ProSystem, A7800 |
| Atari Jaguar | BigPEmu, Virtual Jaguar |
| TurboGrafx-16 | Mednafen, Ootake |
| Neo Geo | FinalBurn Neo, MAME |
| 3DO | 4DO, Opera |
| Multi-system | RetroArch (with cores for all systems) |

This information will be accessible via a "Recommended Emulators" menu item or info panel.

---

## 9. Legal Disclaimer

### 9.1 Disclaimer Text (displayed on first launch and in About)
```
LEGAL DISCLAIMER

This software is a tool for organizing and downloading ROM files from
Internet Archive, a non-profit digital library.

IMPORTANT:
- Only download ROMs for games you legally own physical copies of.
- Downloading copyrighted material without owning the original may be
  illegal in your jurisdiction.
- This software does not host, store, or distribute any ROM files.
- The developers of this software are not responsible for how you
  use this tool.
- By using this software, you agree to comply with all applicable
  laws and regulations regarding ROM usage in your country.

Internet Archive hosts these files for preservation and research
purposes. Please respect copyright holders and support game
developers by purchasing games you enjoy.

[  ] I understand and accept these terms

                                    [Cancel]  [Accept]
```

### 9.2 Implementation
- Show disclaimer dialog on first launch
- Require acceptance before app can be used
- Store acceptance in config file
- Include disclaimer in About dialog
- Add "Legal" menu item to re-read disclaimer

---

## 10. MVP Scope (Phase 1)

### 10.1 Included in MVP
- [x] Python/PyQt6 Windows desktop application
- [ ] System browser sidebar with all supported systems
- [ ] Internet Archive search and browse
- [ ] Game list with sortable columns (title, genre, type, region, size)
- [ ] Basic filters (system, region, genre)
- [ ] Single and batch ROM downloads with progress
- [ ] Folder organization by system
- [ ] SQLite metadata storage
- [ ] Download folder selection
- [ ] Multi-region support with USA priority
- [ ] Legal disclaimer on first launch
- [ ] Recommended emulators info page

### 10.2 Post-MVP (Phase 2+)
- [ ] Download queue with pause/resume
- [ ] Import existing ROM library
- [ ] Advanced search filters
- [ ] Game favorites and tags
- [ ] Collection statistics and reports
- [ ] Export/backup library data
- [ ] macOS and Linux support
- [ ] Auto-update functionality
- [ ] Metadata editing UI

---

## 11. Dependencies

### 11.1 Python Packages
```
PyQt6>=6.4.0
requests>=2.28.0
aiohttp>=3.8.0
aiosqlite>=0.18.0
py7zr>=0.20.0      # 7z extraction
rarfile>=4.0       # RAR extraction
python-dateutil>=2.8.0
```

### 11.2 System Requirements
- Windows 10/11
- Python 3.10+ (bundled with PyInstaller for distribution)
- 100MB disk space (for application)
- Internet connection

---

## 12. Success Metrics

- Successfully browse all 30+ supported systems
- Download ROMs from Internet Archive
- Organize files in clean system-based folder structure
- Retrieve and store accurate metadata
- Sort and filter by title, genre, game type, region
- User can find and download any title within 3 clicks
- Legal disclaimer properly displayed and acknowledged

---

## 13. Game Type Categories

For sorting and filtering purposes:

- Action
- Action-Adventure
- Adventure
- Beat 'em Up
- Educational
- Fighting
- Horror
- Music/Rhythm
- Platformer
- Puzzle
- Racing
- RPG
- Shooter
- Simulation
- Sports
- Strategy
- Visual Novel
- Other

---

## 14. Region Codes

| Code | Region | Priority |
|------|--------|----------|
| USA | United States | 1 (highest) |
| EUR / Europe | Europe | 2 |
| JPN / Japan | Japan | 3 |
| World | Worldwide | 4 |
| PAL | PAL regions | 5 |
| Other | Other variants | 6 |

---

*Document Version: 2.0*
*Created: 2026-01-29*
*Last Updated: 2026-01-29*
*Status: Refined - Ready for Development*
