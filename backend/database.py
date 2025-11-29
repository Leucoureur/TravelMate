"""
Database connection and initialization
"""
import sqlite3
from config import settings

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(settings.DATABASE_URL, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sessions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Destinations table
    c.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT NOT NULL,
            city_code TEXT,
            description TEXT,
            best_months TEXT,
            avg_daily_cost REAL,
            flight_cost_estimate REAL,
            category TEXT,
            image_url TEXT,
            latitude REAL,
            longitude REAL,
            rating REAL DEFAULT 4.0
        )
    """)
    
    # Reviews table
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            destination_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            title TEXT,
            content TEXT,
            travel_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            helpful_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (destination_id) REFERENCES destinations(id)
        )
    """)
    
    # Trips table
    c.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            destination_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            num_travelers INTEGER DEFAULT 1,
            total_cost REAL,
            flight_price REAL,
            hotel_price REAL,
            status TEXT DEFAULT 'planned',
            share_token TEXT UNIQUE,
            is_public INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (destination_id) REFERENCES destinations(id)
        )
    """)
    
    # Favorites table
    c.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER,
            destination_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, destination_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (destination_id) REFERENCES destinations(id)
        )
    """)
    
    conn.commit()
    conn.close()