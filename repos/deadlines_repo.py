from datetime import datetime
from typing import Optional, Tuple, Union, Dict, List
from .base_repo import BaseRepo

from database_handler.database_handler import DatabaseHandler

class DeadlinesRepo(BaseRepo):
    def __init__(self, db_handler: DatabaseHandler):
        super().__init__('Deadlines', db_handler)
        self.allowed_columns = [
            'deadline_id',
            'case_id',
            'description',
            'due_date',
            'deadline_type',
            'status',
            'completed',
            'created_at',
            'updated_at',
            'deactivated_at'
        ]

    def get_all_deadlines(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} ORDER BY due_date'
        )

    def get_deadline_by_id(self, id_value: id, id_field: str='deadline_id') -> Tuple[bool, Union[dict, None, Exception]]:
        return self._get_record_by_id(id_field, id_value)
    
    def get_open_deadlines(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE completed=0 ORDER BY due_date'
        )
    
    def get_open_deadlines_by_case(self, case_id: int) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE completed=0 and case_id=? ORDER BY due_date',
            (case_id,)
        )

    def insert_deadline(self, deadline_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self.insert_new_record(deadline_data)

    def update_deadline(self, deadline_data: dict, id_value:int, id_field:str='deadline_id') -> Tuple[bool, Union[int, Exception]]:
        return self.update_by_id(id_field, id_value, deadline_data)

    def mark_deadline_completed(self, id_value:int, id_field:str='deadline_id', completed_at:Optional[str] = None) -> Tuple[bool, Union[int, Exception]]:
        if completed_at is None:
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updates = {
            'completed':0,
            'status': 'Done',
            'completed_at':completed_at
        }
        return self.update_by_id(
            id_field,
            id_value,
            updates
        )
