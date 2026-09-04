import sqlite3
from pathlib import Path


# Get the backend folder
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database file path
DB_PATH = BASE_DIR / "database" / "universal_log_preprocessor.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    conn = sqlite3.connect(DB_PATH)

    # Allows rows to be accessed like dictionaries
    conn.row_factory = sqlite3.Row

    return conn


def initialize_database():
    """
    Create the processed_logs table if it does not already exist.
    """

    conn = get_connection()

    cursor = conn.cursor()

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

    conn.commit()

    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()