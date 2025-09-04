from typing import Tuple, Union
from .base_repo import BaseRepo

class DeadlinesRepo(BaseRepo):
    def __init__(self, table_name='Deadlines', db_path = None):
        super().__init__(table_name, db_path)

    def get_all_deadlines(self) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} ORDER BY due_date'
        )

    def get_deadline_by_id(self, deadline_data: dict) -> Tuple[bool, Union[dict, None, Exception]]:
        return self._run_query_one(
            f'SELECT * FROM {self.table_name} WHERE deadline_id = ?',
            (deadline_data['deadline_id'],)
        )
    
    def get_open_deadlines(self) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE completed=0 ORDER BY due_date'
        )
    
    def get_open_deadlines_by_case(self, deadline_data: dict) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE completed=0 and case_id=? ORDER BY due_date',
            (deadline_data['case_id'],)
        )

    def insert_deadline(self, deadline_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            INSERT INTO {self.table_name} (
                case_id,
                description,
                due_date,
                type,
                status,
                completed,
                created_at,
                updated_at,
                completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                deadline_data['case_id'],
                deadline_data['description'],
                deadline_data['due_date'],
                deadline_data['type'],
                deadline_data['status'],
                deadline_data['completed'],
                deadline_data['created_at'],
                deadline_data['updated_at'],
                deadline_data['completed_at']
            )
        )

    def update_deadline(self, deadline_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            UPDATE {self.table_name}
            SET
                case_id=?,
                description=?,
                due_date=?,
                type=?,
                status=?,
                completed=?,
                created_at=?,
                updated_at=?,
                completed_at=?
            WHERE deadline_id=?
            """,
            (
                deadline_data['case_id'],
                deadline_data['description'],
                deadline_data['due_date'],
                deadline_data['type'],
                deadline_data['status'],
                deadline_data['completed'],
                deadline_data['created_at'],
                deadline_data['updated_at'],
                deadline_data['completed_at'],
                deadline_data['deadline_id']
            )
        )

    def mark_deadline_completed(self, deadline_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            UPDATE {self.table_name}
            SET
            completed = 1,
            status = 'Done',
            updated_at = ?,
            completed_at = ?
            WHERE deadline_id = ?
            """,
            (
                deadline_data['updated_at'],
                deadline_data['completed_at'],
                deadline_data['deadline_id']
                )
        )
