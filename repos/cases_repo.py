from typing import Tuple, Union
from .base_repo import BaseRepo

class CasesRepo(BaseRepo):
    
    def __init__(self, table_name='Cases', db_path = None):
        super().__init__(table_name, db_path)

    def get_all_cases(self) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name}'
        )

    def get_case_by_id(self, case_data: dict) -> Tuple[bool, Union[dict, None, Exception]]:
        return self._run_query_one(
            f'SELECT * FROM {self.table_name} WHERE case_id = ?',
            (case_data['case_id'],)
        )
    
    def get_cases_by_client(self, case_data: dict) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT cs.* FROM {self.table_name} WHERE client_id=? ',
            (case_data['client_id'],)
        )
    
    def get_open_cases_by_client(self, case_data: dict) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE client_id=? AND is_open=1',
            (case_data['client_id'],)
        )
    
    def get_cases_by_jurisdiction(self, case_data: dict) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE jurisdiction=?',
            (case_data['jurisdiction'],)
        )
    
    def get_cases_by_procedure(self, case_data: dict) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE procedure_type=?',
            (case_data['procedure_type'],)
        )

    def get_cases_by_ipr_type(self, case_data: dict) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE ipr_type=?',
            (case_data['ipr_type'],)
        )
    
    def get_cases_by_status(self, case_data: dict) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE status=?',
            (case_data['status'],)
        )

    def insert_case(self, case_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            INSERT INTO {self.table_name} (
                case_type, procedure_type, ipr_type,
                client_id, client_ref,
                title,
                jurisdiction, filing_date, filing_number, status,
                notes,
                is_open,
                created_at, updated_at, closed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_data['case_type'], case_data['procedure_type'], case_data['ipr_type'],
                case_data['client_id'], case_data['client_ref'],
                case_data['title'],
                case_data['jurisdiction'], case_data['filing_date'], case_data['filing_number'],
                case_data['status'],
                case_data['notes'],
                case_data['is_open'],
                case_data['created_at'], case_data['updated_at'], case_data['closed_at']
            )
        )

    def update_case(self, case_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            UPDATE {self.table_name}
            SET
                case_type=?, procedure_type=?, ipr_type=?,
                client_id=?, client_ref=?,
                title=?,
                jurisdiction=?, filing_date=?, filing_number=?, status=?,
                notes=?,
                is_open=?,
                created_at=?, updated_at=?, closed_at=?
            WHERE case_id = ?
            """,
            (
                case_data['case_type'], case_data['procedure_type'], case_data['ipr_type'],
                case_data['client_id'], case_data['client_ref'],
                case_data['title'],
                case_data['jurisdiction'], case_data['filing_date'], case_data['filing_number'],
                case_data['status'],
                case_data['notes'],
                case_data['is_open'],
                case_data['created_at'], case_data['updated_at'], case_data['closed_at'],
                case_data['case_id']
            )
        )

    def close_case(self, case_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            UPDATE {self.table_name}
            SET
            is_open = 0,
            closed_at = ?
            WHERE case_id = ?
            """,
            (
                case_data['closed_at'],
                case_data['case_id']
                )
        )
