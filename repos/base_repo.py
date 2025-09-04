import sqlite3
from typing import Optional, List, Tuple, Union
from database_handler.database_handler import DatabaseHandler

class BaseRepo:

    def __init__(self, table_name:str, db_path: Optional[str] = None):
        self.db_path = db_path
        self.table_name = table_name

    def _run_query(self, query: str, params: tuple = ()) -> Tuple[bool, Union[List[dict], Exception]]:
        try:
            with DatabaseHandler(self.db_path) as conn:
                cursor = conn.cursor()
                rows = cursor.execute(query, params)
            return (True, [dict(row) for row in rows])
        except sqlite3.Error as e:
            return (False, e)

    def _run_query_one(self, query: str, params: tuple = ()) -> Tuple[bool, Union[dict, None, Exception]]:
        try:
            with DatabaseHandler(self.db_path) as conn:
                cursor = conn.cursor()
                row = cursor.execute(query, params).fetchone()
            return (True, dict(row)) if row else (True, None)
        except sqlite3.Error as e:
            return (False, e)

    def _run_modify(self, query: str, params: tuple = ()) -> Tuple[bool, Union[int, Exception]]:
        try:
            with DatabaseHandler(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
            return (True, cursor.lastrowid)
        except sqlite3.Error as e:
            return (False, e)