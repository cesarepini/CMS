import sqlite3

from typing import Dict, Optional, List, Tuple, Union
from database_handler.database_handler import DatabaseHandler


class BaseRepo:

    def __init__(self, table_name:str, db_handler: DatabaseHandler):
        self.db_handler = db_handler
        self.table_name = table_name

    def _run_query(
            self,
            query: str,
            params: tuple = ()
            ) -> Tuple[bool, Union[List[Dict], Exception]]:
        try:
            with self.db_handler as conn:
                cursor = conn.cursor()
                rows = cursor.execute(query, params)
            return (True, [dict(row) for row in rows])
        except sqlite3.Error as e:
            return (False, e)

    def _run_query_one(
            self,
            query: str,
            params: tuple = ()
            ) -> Tuple[bool, Union[dict, None, Exception]]:
        try:
            with self.db_handler as conn:
                cursor = conn.cursor()
                row = cursor.execute(query, params).fetchone()
            return (True, dict(row)) if row else (True, None)
        except sqlite3.Error as e:
            return (False, e)
        
    def _get_record_by_id(self, id_field:str, id_value:int) -> Tuple[bool, Union[dict, None, Exception]]:
        query = f'SELECT * FROM {self.table_name} WHERE {id_field} = ?'
        return self._run_query_one(query, (id_value,))

    def _run_modify(
            self,
            query: str,
            params: tuple = ()
            ) -> Tuple[bool, Union[int, Exception]]:
        try:
            with self.db_handler as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row_id = cursor.lastrowid
            return (True, row_id)
        except sqlite3.Error as e:
            return (False, e)
        
    def insert_new_record(
            self,
            data:dict
            ) -> Tuple[bool, Union[int, Exception]]:
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = tuple(data.values())
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        return self._run_modify(query, values)
        
    def update_by_id(self,
                    id_field: str,
                    id_value: int,
                    updates: dict
                    ) -> Tuple[bool, Union[int, Exception]]:
        set_clause = ", ".join([f"{col}=?" for col in updates.keys()])
        values = tuple(updates.values()) + (id_value,)
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_field} = ?"
        return self._run_modify(query, values)

    # TODO: block this function for most tables    
    def delete_by_id(
            self,
            id_field: str,
            id_value: int
            ) -> Tuple[bool, Union[int, Exception]]:
        query = f"DELETE FROM {self.table_name} WHERE {id_field} = ?"
        return self._run_modify(query, (id_value,))