# Product Requirements Document (PRD)
# ROMs Downloader and Organizer

## 1. Overview

### 1.1 Product Vision
A desktop application that allows users to browse, download, and organize video game ROMs from Internet Archive. The app provides a comprehensive catalog of titles from Nintendo and PlayStation systems, with robust metadata management and organization features.

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
| System | Abbreviation | Generation |
|--------|--------------|------------|
| Nintendo Entertainment System | NES | 3rd |
| Super Nintendo Entertainment System | SNES | 4th |
| Nintendo 64 | N64 | 5th |
| GameCube | GCN | 6th |
| Wii | Wii | 7th |
| Game Boy | GB | Handheld |
| Game Boy Color | GBC | Handheld |
| Game Boy Advance | GBA | Handheld |
| Nintendo DS | NDS | Handheld |
| Nintendo 3DS | 3DS | Handheld |

### 2.2 PlayStation Systems
| System | Abbreviation | Generation |
|--------|--------------|------------|
| PlayStation | PS1/PSX | 5th |
| PlayStation 2 | PS2 | 6th |
| PlayStation 3 | PS3 | 7th |
| PlayStation Portable | PSP | Handheld |
| PlayStation Vita | PSV | Handheld |

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
  - Rating

### 3.2 Download Management
- **Source**: Internet Archive ROM collections
- **Queue System**: Add multiple ROMs to download queue
- **Progress Tracking**: Real-time download progress per item
- **Pause/Resume**: Ability to pause and resume downloads
- **Retry Logic**: Automatic retry on failed downloads
- **Bandwidth Control**: Optional download speed limiting

### 3.3 Folder Organization
- **Custom Download Location**: User-selectable root download folder
- **Folder Structure Options**:
  ```
  Option 1: By System
  /ROMs
    /NES
    /SNES
    /PS1
    ...

  Option 2: By Genre
  /ROMs
    /Action
    /RPG
    /Sports
    ...

  Option 3: By System then Genre
  /ROMs
    /NES
      /Action
      /RPG
    /SNES
      /Action
      /RPG
    ...
  ```
- **File Naming**: Clean, consistent file naming conventions
- **Duplicate Detection**: Warn when ROM already exists

### 3.4 Metadata Management
- **Auto-fetch Metadata**: Pull metadata from Internet Archive and/or external databases
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
  - Box Art / Cover Image
  - Rating (if available)
  - File Hash (for verification)
- **Metadata Format**: JSON sidecar files or SQLite database
- **Manual Edit**: Allow users to edit/correct metadata

### 3.5 Library Management (Existing ROMs)
- **Import Existing**: Scan user's existing ROM folders
- **Auto-identify**: Attempt to identify ROMs by filename/hash
- **Organize Existing**: Move/rename existing ROMs to match organization scheme
- **Collection Stats**: Show library statistics (total games, per system, etc.)

---

## 4. User Interface

### 4.1 Main Views
1. **Browse View**: Grid/List of available ROMs to download
2. **Library View**: User's downloaded/imported ROMs
3. **Downloads View**: Active and queued downloads
4. **Settings View**: App configuration

### 4.2 UI Components
- System selector sidebar
- Search bar with filters
- Game card (thumbnail, title, system, genre)
- Detail panel (full metadata, download button)
- Download queue panel
- Progress indicators

### 4.3 Technology Options
- **Desktop App**: Electron, Tauri, or Python (PyQt/Tkinter)
- **Web App**: React/Vue with local backend
- **CLI**: Python/Node.js command-line interface

---

## 5. Technical Architecture

### 5.1 Data Sources
- **Primary**: Internet Archive API
  - Collection: Various ROM archives
  - Endpoints: Search, metadata, download URLs
- **Secondary** (optional):
  - TheGamesDB API (metadata enrichment)
  - IGDB API (metadata enrichment)
  - No-Intro DAT files (verification)

### 5.2 Local Storage
- **Database**: SQLite for game catalog and user library
- **Config**: JSON/YAML for user preferences
- **Cache**: Local cache for thumbnails and metadata

### 5.3 Key Components
```
┌─────────────────────────────────────────────────┐
│                   UI Layer                       │
│  (Browse | Library | Downloads | Settings)       │
├─────────────────────────────────────────────────┤
│                 Service Layer                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Catalog  │ │ Download │ │    Organizer     │ │
│  │ Service  │ │ Manager  │ │    Service       │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
├─────────────────────────────────────────────────┤
│                  Data Layer                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Internet │ │  Local   │ │   File System    │ │
│  │ Archive  │ │ Database │ │    Manager       │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 6. Internet Archive Integration

### 6.1 Search & Browse
- Query IA collections for ROM files
- Parse metadata from IA item records
- Handle pagination for large result sets

### 6.2 Download Process
1. Get item metadata from IA
2. Extract download URL for ROM file
3. Download with progress tracking
4. Verify file integrity (if hash available)
5. Extract if compressed (zip, 7z, rar)
6. Apply naming convention
7. Store metadata locally

### 6.3 Rate Limiting
- Respect IA rate limits
- Implement request throttling
- Queue management for bulk downloads

---

## 7. Configuration Options

### 7.1 User Preferences
- Download folder location
- Folder organization scheme
- File naming convention
- Preferred regions (priority order)
- Auto-extract compressed files (yes/no)
- Keep original archives (yes/no)
- Download speed limit
- Concurrent downloads limit

### 7.2 Default Settings
```json
{
  "downloadPath": "~/ROMs",
  "organizationScheme": "by-system",
  "namingConvention": "{title} ({region})",
  "preferredRegions": ["USA", "EUR", "JPN"],
  "autoExtract": true,
  "keepArchives": false,
  "maxConcurrentDownloads": 3,
  "speedLimitKbps": 0
}
```

---

## 8. MVP Scope (Phase 1)

### 8.1 Included in MVP
- [ ] Basic UI with system browser
- [ ] Internet Archive search and browse
- [ ] Single ROM download with progress
- [ ] Basic folder organization (by system)
- [ ] Metadata storage (JSON sidecar)
- [ ] Sort by title, genre, game type
- [ ] Settings for download folder

### 8.2 Post-MVP (Phase 2+)
- [ ] Download queue with multiple concurrent downloads
- [ ] Import existing ROM library
- [ ] Advanced metadata from external APIs
- [ ] Box art/thumbnail display
- [ ] Emulator integration (launch games)
- [ ] Collection statistics and reports
- [ ] Export/backup library data

---

## 9. Success Metrics

- Successfully browse all supported systems
- Download ROMs from Internet Archive
- Organize files in clean folder structure
- Retrieve and store accurate metadata
- Sort and filter by multiple criteria
- User can find and download any title within 3 clicks

---

## 10. Open Questions

1. **Technology Stack**: Desktop app (Electron/Tauri/Python) or Web app?
2. **Metadata Source Priority**: Internet Archive only, or integrate external DBs?
3. **Region Handling**: Download all regions or user-preferred only?
4. **File Verification**: Implement hash verification against No-Intro DATs?
5. **Legal Disclaimer**: How to handle legal notices regarding ROM usage?
6. **Offline Capability**: Should the catalog be cached for offline browsing?

---

## 11. Appendix

### 11.1 Game Type Categories
- Action
- Adventure
- Fighting
- Platformer
- Puzzle
- Racing
- RPG (Action RPG, JRPG, Strategy RPG, etc.)
- Shooter
- Simulation
- Sports
- Strategy
- Other

### 11.2 Region Codes
- USA (U)
- Europe (E)
- Japan (J)
- World (W)
- Other regional variants

---

*Document Version: 1.0*
*Created: 2026-01-29*
*Status: Draft - Pending Review*
