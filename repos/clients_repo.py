from typing import Tuple, Union
from repos.base_repo import BaseRepo

class ClientsRepo(BaseRepo):
    def __init__(self, db_path=None):
        super().__init__("Clients", db_path)

    def get_all_clients(self) -> Tuple[bool, Union[list, Exception]]:
        return self._run_query(
            f'SELECT * FROM {self.table_name} ORDER BY name'
        )

    def get_client_by_id(self, client_data: dict) -> Tuple[bool, Union[dict, None, Exception]]:
        return self._run_query_one(
            f'SELECT * FROM {self.table_name} WHERE client_id = ?',
            (client_data['client_id'],)
        )

    def get_active_clients(self):
        return self._run_query(
            f'SELECT * FROM {self.table_name} WHERE is_active=1 ORDER BY NAME'
        )

    def insert_client(self, client_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            INSERT INTO {self.table_name} (
                name, address, zip_code, city, country,
                email, phone, vat_number, payment_term, notes,
                is_active, created_at, updated_at, deactivated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client_data['name'],
                client_data['address'],
                client_data['zip_code'],
                client_data['city'],
                client_data['country'],
                client_data['email'],
                client_data['phone'],
                client_data['vat_number'],
                client_data['payment_term'],
                client_data['notes'],
                client_data['is_active'],
                client_data['created_at'],
                client_data['updated_at'],
                client_data['deactivated_at']
            )
        )

    def update_client(self, client_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            UPDATE {self.table_name}
            SET
                name=?, address=?, zip_code=?, city=?, country=?,
                email=?, phone=?, vat_number=?, payment_term=?, notes=?,
                is_active=?, updated_at=?, deactivated_at=?
            WHERE client_id=?
            """,
            (
                client_data['name'],
                client_data['address'],
                client_data['zip_code'],
                client_data['city'],
                client_data['country'],
                client_data['email'],
                client_data['phone'],
                client_data['vat_number'],
                client_data['payment_term'],
                client_data['notes'],
                client_data['is_active'],
                client_data['updated_at'],
                client_data['deactivated_at'],
                client_data['client_id']
            )
        )

    def deactivate_client(self, client_data: dict) -> Tuple[bool, Union[int, Exception]]:
        return self._run_modify(
            f"""
            UPDATE {self.table_name}
            SET is_active = 0, deactivated_at=?
            WHERE client_id = ?
            """,
            (
                client_data['deactivated_at'],
                client_data['client_id']
            )
        )
