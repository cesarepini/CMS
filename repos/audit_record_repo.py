from datetime import datetime
from typing import Optional, Tuple, Union, Dict, List
from .base_repo import BaseRepo

from database_handler.database_handler import DatabaseHandler

class AuditRecordsRepo(BaseRepo):
    def __init__(self, db_handler: DatabaseHandler):
        super().__init__('Deadlines', db_handler)
        self.allowed_columns = [
            'audit_field_id',
            'table_name',
            'action',
            'table_record_id',
            'new_value',
            'timestamp',
            'hash',
            'previous_hash'
        ]

    def get_all_audit_records(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} ORDER BY timestamp'
        )

    def get_audit_record_by_id(self, id_value: id, id_field: str='audit_record_id') -> Tuple[bool, Union[dict, None, Exception]]:
        return self._get_record_by_id(id_field, id_value)
    
    def insert_audit_record(self, audit_record_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self.insert_new_record(audit_record_data)