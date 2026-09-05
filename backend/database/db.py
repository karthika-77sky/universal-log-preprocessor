import sqlite3
from pathlib import Path


# ============================================================
# DATABASE PATH
# ============================================================

# Get the backend folder
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database file path
DB_PATH = BASE_DIR / "database" / "universal_log_preprocessor.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    conn = sqlite3.connect(DB_PATH)

    # Allows rows to be accessed like dictionaries
    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """
    Create all required database tables if they do not already exist.
    """

    conn = get_connection()

    cursor = conn.cursor()


    # ========================================================
    # TABLE 1: ORIGINAL PROCESSED LOGS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            log_id TEXT NOT NULL UNIQUE,

            filename TEXT NOT NULL,

            detected_format TEXT NOT NULL,

            parsed_fields TEXT NOT NULL,

            raw_log TEXT NOT NULL,

            confidence TEXT NOT NULL,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    # ========================================================
    # TABLE 2: UNIVERSAL NORMALIZED EVENTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS normalized_events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event_id TEXT NOT NULL UNIQUE,

            source_filename TEXT NOT NULL,

            timestamp TEXT,

            event_type TEXT,

            severity TEXT,

            user TEXT,

            source_format TEXT NOT NULL,

            message TEXT,

            parsed_fields TEXT NOT NULL,

            raw_event TEXT NOT NULL,

            confidence TEXT NOT NULL,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    # Save changes
    conn.commit()

    conn.close()

    print("Database initialized successfully.")


# ============================================================
# RUN DATABASE INITIALIZATION DIRECTLY
# ============================================================

if __name__ == "__main__":
    initialize_database()