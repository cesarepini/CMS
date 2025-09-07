from datetime import datetime
from typing import Tuple, Union, List, Dict

from repos.clients_repo import ClientsRepo
from repos.cases_repo import CasesRepo

class ClientsService():
    def __init__(self, clients_repo: ClientsRepo, cases_repo:CasesRepo):
        self.clients_repo = clients_repo
        self.cases_repo = cases_repo

    def get_all_clients(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.clients_repo.get_all_clients()
    
    def get_active_clients(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.clients_repo.get_active_clients()
    
    def get_client_by_id(self, client_id: int) -> Tuple[bool, Union[Dict, None, Exception]]:
        return self.clients_repo.get_client_by_id(client_id, 'client_id')
    
    def insert_client(self, client_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        if 'name' not in client_data or not client_data['name']:
            return (False, ValueError('Client name is required.'))
        if 'country' not in client_data or not client_data['country']:
            return (False, ValueError('Country is required.'))
        if len(client_data['country']) != 2:
            return (False, ValueError('Country must be two letters according to WIPO standard.'))
        optional_fields = [
            'address', 'zip_code', 'city',
            'email', 'phone', 'vat_number',
            'payment_term', 'notes'
            ]
        for field in optional_fields:
            client_data[field] = client_data.get(field) or None
        client_data['is_active'] = 1
        client_data['deactivated_at'] = None
        client_data['created_at'] = client_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.clients_repo.insert_client(
            client_data
        )
    
    def update_client(self, client_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        if 'client_id' not in client_data or not client_data['client_id']:
            return (False, ValueError('Client ID must be provided.'))
        if 'name' not in client_data or not client_data['name']:
            return (False, ValueError('Client name is required.'))
        if 'country' not in client_data or not client_data['country']:
            return (False, ValueError('Country is required.'))
        if len(client_data['country']) != 2:
            return (False, ValueError('Country must be two letters according to WIPO standard.'))
        optional_fields = [
            'address', 'zip_code', 'city',
            'email', 'phone', 'vat_number',
            'payment_term', 'notes'
            ]
        for field in optional_fields:
            client_data[field] = client_data.get(field) or None
        client_data['is_active'] = 1
        client_data['deactivated_at'] = None
        client_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_id = client_data.pop('client_id')
        return self.clients_repo.update_client(client_data, client_id)
    
    def deactivate_client(self, client_id: int) -> Tuple[bool, Union[int, str, Exception]]:
        success, open_cases = self.cases_repo.get_open_cases_by_client(client_id)
        if not success:
            return False, open_cases
        if open_cases and len(open_cases) > 0:
            return False, "Client has open cases and cannot be deactivated."

        return self.clients_repo.deactivate_client(client_id)