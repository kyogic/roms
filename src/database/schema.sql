-- ROMs Downloader Database Schema

-- Systems table
CREATE TABLE IF NOT EXISTS systems (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    abbreviation TEXT NOT NULL,
    manufacturer TEXT,
    generation TEXT
);

-- Games catalog (from Internet Archive)
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ia_identifier TEXT,
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
    file_name TEXT,
    file_hash TEXT,
    download_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ia_identifier, file_name)
);

-- User's library (downloaded ROMs)
CREATE TABLE IF NOT EXISTS library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER REFERENCES games(id),
    file_path TEXT NOT NULL UNIQUE,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE
);

-- Download queue
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER REFERENCES games(id),
    status TEXT DEFAULT 'pending',
    progress REAL DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Indexes for fast sorting/filtering
CREATE INDEX IF NOT EXISTS idx_games_system ON games(system_id);
CREATE INDEX IF NOT EXISTS idx_games_genre ON games(genre);
CREATE INDEX IF NOT EXISTS idx_games_title ON games(title);
CREATE INDEX IF NOT EXISTS idx_games_region ON games(region);
CREATE INDEX IF NOT EXISTS idx_games_ia_identifier ON games(ia_identifier);
CREATE INDEX IF NOT EXISTS idx_library_game_id ON library(game_id);
CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status);
