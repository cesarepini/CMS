import hashlib
import sqlite3
from pathlib import Path
from typing import Optional, Tuple, Union, List

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "patent_case_manager.db"
MIGRATIONS_DIR = BASE_DIR / "migrations"


class DatabaseHandler:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)  # ✅ ensure path exists
        self.conn: Optional[sqlite3.Connection] = None
        self.conn = None

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        return self.conn
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.conn:
            try:
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            finally:
                self.conn.close()
            self.conn = None

    def init_database(self)->None:
        (
            migrations_applied,
            number_migrations_applied,
            migrations_applied_names
            ) = self._apply_migrations()

        # for name in migrations_applied_names:
        #     self._log_migrations(
        #         migration_applied=migrations_applied,
        #         log_detail=name
        #     )

    # def _log_audit(
    #         self,
    #         log_level:str,
    #         action: str,
    #         details: str,
    #         user_id: int
    #         ) -> None:
    #     """
    #     Insert a log entry into Audit_Log.
    #     """
    #     try:
    #         with self as conn:
    #             cursor = conn.cursor()
    #             cursor.execute('SELECT hash FROM Audit_Log ORDER BY audit_log_id DESC LIMIT 1')
    #             record = cursor.fetchone()
    #             prev_hash = record[0] if record else ''
    #             hashed_string = self._compute_audit_hash(
    #                 {
    #                     'log_level':log_level,
    #                     'action':action,
    #                     'details':details,
    #                     'user_id':user_id,
    #                     'previous_hash':prev_hash
    #                 }
    #             )
    #             cursor = conn.cursor()
    #             cursor.execute(
    #                 """
    #                 INSERT INTO Audit_Log (user_id, log_level, action, details, hash, previous_hash, logged_at)
    #                 VALUES (?, ?, ?, ?, ?, ?, strftime('%s','now'))
    #                 """,
    #                 (user_id, log_level, action, details, hashed_string, prev_hash)
    #             )
    #     except sqlite3.Error as e:
    #         #TODO:stub later out to logger file
    #         print(f'Error occured: {e}')

    # def _compute_audit_hash(self, data: dict) -> str:
    #     canonical_string = '|'.join(str(data[k]) for k in sorted(data))
    #     return hashlib.sha256(canonical_string.encode()).hexdigest()

    def _apply_migrations(self) -> Tuple[bool, int, Union[List[str], str]]:
        """Apply all migrations from the migrations folder in order."""
        try:
            with self as conn:
                cursor = conn.cursor()
        # Ensure migrations table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT UNIQUE NOT NULL,
                        applied_at INTEGER NOT NULL
                    )
                """)
                conn.commit()

                # Check applied migrations
                cursor.execute("SELECT filename FROM schema_migrations")
                applied = {row["filename"] for row in cursor.fetchall()}
                new_migrations_file_names = list()
                # Apply new migrations
                for migration_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
                    if migration_file.name not in applied:
                        print(f"Applying migration: {migration_file.name}")
                        with open(migration_file, "r", encoding="utf-8") as f:
                            sql = f.read()
                        cursor.executescript(sql)
                        cursor.execute(
                            "INSERT INTO schema_migrations (filename, applied_at) VALUES (?, strftime('%s','now'))",
                            (migration_file.name,)
                        )
                        conn.commit()
                        new_migrations_file_names.append(migration_file.name)
                print(f'✅ All migrations applied: {new_migrations_file_names}')
                
                return (True, len(new_migrations_file_names), new_migrations_file_names)
        except sqlite3.Error as e:
            print(e)
            return (False, 0, f'Database initialization failed. Error {e}')
        
    # def _log_migrations(self, migration_applied: bool, log_detail: str) -> None:
    #     if migration_applied:
    #         self._log_audit(
    #             action= 'Migration applied',
    #             log_level='INFO',
    #             details= f'migration {log_detail} applied',
    #             user_id=1
    #             )
    #     else:
    #         self._log_audit(
    #             action= 'Migration applied failed',
    #             log_level='ERROR',
    #             details= f'Error: {log_detail}',
    #             user_id=1
    #             )
    
    @classmethod
    def run_init_database_static(cls):
        return cls().init_database()

# DEBUG
if __name__ == "__main__":
    db = DatabaseHandler()
    db.init_database()