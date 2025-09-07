from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from repos.base_repo import BaseRepo

from database_handler.database_handler import DatabaseHandler

class CasesRepo(BaseRepo):
    
    def __init__(self, db_handler: DatabaseHandler):
        super().__init__('Cases', db_handler)

        self.allowed_columns = [
            'case_id',
            'case_type',
            'procedure_type',
            'ipr_type',
            'client_id',
            'client_ref',
            'title',
            'address',
            'jurisdiction',
            'filing_date',
            'filing_number',
            'status',
            'notes',
            'is_open',
            'created_at',
            'updated_at',
            'closed_at'
        ]

    def get_all_cases(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name}'
        )

    def get_case_by_id(self, id_value:int, id_field: str = 'case_id') -> Tuple[bool, Union[dict, None, Exception]]:
        return self._get_record_by_id(id_field, id_value)
    
    def get_open_cases(self) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(f'SELECT * FROM {self.table_name} WHERE is_open=1')

    def get_cases_by_client(self, client_id: int) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT cs.* FROM {self.table_name} WHERE client_id=? ',
            (client_id,)
        )
    
    def get_open_cases_by_client(self, client_id: int) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE client_id=? AND is_open=1',
            (client_id,)
        )
    
    def get_cases_by_jurisdiction(self, jurisdiction: str) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE jurisdiction=?',
            (jurisdiction,)
        )
    
    def get_cases_by_procedure(self, procedure_type: str) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE procedure_type=?',
            (procedure_type,)
        )

    def get_cases_by_ipr_type(self, ipr_type: str) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE ipr_type=?',
            (ipr_type,)
        )
    
    def get_cases_by_status(self, status: str) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE status=?',
            (status,)
        )

    def insert_case(self, case_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self.insert_new_record(case_data)

    def update_case(self, case_data: dict, id_value:int, id_field:str = 'case_id') -> Tuple[bool, Union[int, Exception]]:
        return self.update_by_id(id_field, id_value, case_data)

    def close_case(
            self,
            id_value:int,
            id_field:str = 'case_id',
            closed_at:Optional[str] = None
            ) -> Tuple[bool, Union[int, Exception]]:
        if closed_at is None:
            closed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updates = {
            'is_open':0,
            'closed_at':closed_at
        }
        return self.update_by_id(id_field, id_value, updates)
