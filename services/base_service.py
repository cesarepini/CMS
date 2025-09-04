# services/base_service.py

from typing import Union, List, Dict, Optional, Tuple
from repos.base_repo import BaseRepo

class BaseService:
    def __init__(self, repo: BaseRepo):
        self.repo = repo

    def _get_all_records(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.repo._run_query(f'SELECT * FROM {self.repo.table_name}')

    def _get_record_by_id(self, record_id: int, id_field: str = "id") -> Tuple[bool, Union[Dict, None, Exception]]:
        return self.repo._run_query_one(
            f'SELECT * FROM {self.repo.table_name} WHERE {id_field} = ?',
            (record_id,)
        )
