from typing import Dict, List, Optional, Tuple, Union
from repos.base_repo import BaseRepo
from datetime import datetime

from database_handler.database_handler import DatabaseHandler

class ClientsRepo(BaseRepo):
    def __init__(self, db_handler: DatabaseHandler):
        super().__init__("Clients", db_handler)

    # --- Querying functions --- #
    def get_all_clients(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} ORDER BY name'
        )

    def get_client_by_id(self, id_value:int, id_field:str = 'client_id') -> Tuple[bool, Union[dict, None, Exception]]:
        return self._get_record_by_id(id_field, id_value)

    def get_active_clients(self):
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE is_active=1 ORDER BY NAME'
        )

    # --- Modifying functions --- #
    def insert_client(self, client_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self.insert_new_record(client_data)

    def update_client(
            self,
            client_data: dict,
            id_value:int,
            id_field:str = 'client_id'
            ) -> Tuple[bool, Union[int, Exception]]:
        return self.update_by_id(id_field, id_value, client_data)

    def deactivate_client(
            self,
            id_value:int,
            id_field:str = 'client_id',
            deactivated_at:Optional[str] = None
            ) -> Tuple[bool, Union[int, Exception]]:
        if deactivated_at is None:
            deactivated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updates = {
            'is_active':0,
            'deactivated_at':deactivated_at
        }
        return self.update_by_id(id_field, id_value, updates)
