# database_handler/database_handler.py

import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple, Union

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "patent_case_manager.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

class DatabaseHandler:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self.init_database()

    def __enter__(self) -> sqlite3.Connection:
        # This will be called by the 'with' statement
        if not self.conn or self.is_closed():
            self.connect()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # We will no longer close the connection here automatically.
        # This allows the connection to persist across multiple 'with' blocks.
        if self.conn and exc_type is None:
            self.conn.commit()
        elif self.conn:
            self.conn.rollback()

    def connect(self) -> None:
        """Establishes a database connection."""
        if not self.conn or self.is_closed():
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False) # Added for Streamlit
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON;")

    def close(self) -> None:
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def is_closed(self) -> bool:
        """Checks if the connection is closed or not initialized."""
        try:
            # Attempting to get the total_changes will raise a ProgrammingError if closed.
            self.conn.total_changes
            return False
        except (sqlite3.ProgrammingError, AttributeError):
            return True

    #TODO: Stub the prints arguments out to return a tuple(Boolen, Union[str, Error]) for logging
    def init_database(self) -> None:
        """Initializes the database and applies migrations."""
        if not self.conn:
            self.connect()
        try:
            with self as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT UNIQUE NOT NULL,
                        applied_at TEXT NOT NULL CHECK(LENGTH(applied_at)=19)
                    )
                """)
                conn.commit()

                cursor.execute("SELECT filename FROM schema_migrations")
                applied = {row["filename"] for row in cursor.fetchall()}
                new_migrations_file_names = []

                for migration_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
                    if migration_file.name not in applied:
                        print(f"Applying migration: {migration_file.name}")
                        with open(migration_file, "r", encoding="utf-8") as f:
                            sql = f.read()
                        cursor.executescript(sql)
                        cursor.execute(
                            "INSERT INTO schema_migrations (filename, applied_at) VALUES (?, datetime(strftime('%s','now'), 'unixepoch'))",
                            (migration_file.name,)
                        )
                        conn.commit()
                        new_migrations_file_names.append(migration_file.name)
                
                if new_migrations_file_names:
                    print(f'✅ Migrations applied: {new_migrations_file_names}')
                else:
                    print('✅ Database schema is up to date.')

        except sqlite3.Error as e:
            print(f'Database initialization failed. Error: {e}')