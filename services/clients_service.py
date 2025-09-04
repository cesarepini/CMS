from typing import Tuple, Union, List, Dict
from services.base_service import BaseService
from repos.clients_repo import ClientsRepo

class ClientService(BaseService):
    def __init__(self, repo):
        super().__init__(repo)
        self.repo : ClientsRepo = repo

    def get_all_clients(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self._get_all_records()
    
    def get_active_clients(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.repo.get_active_clients()
    
    def get_client_by_id(self, client_id: int) -> Tuple[bool, Union[Dict, None, Exception]]:
        return self._get_record_by_id(client_id, 'client_id')
    
    def insert_client(self, client_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        if 'name' not in client_data or not client_data['name']:
            return (False, ValueError('Client name is required.'))
        if 'country' not in client_data or not client_data['country']:
            return (False, ValueError('Country is required.'))
        if len(client_data['country']) != 2:
            return (False, ValueError('Country must be two letters according to WIPO standard.'))
        if (
            'created_at' not in client_data or
            not client_data['created_at'] or
            'updated_at' not in client_data or
            client_data['updated_at']
        ):
            return (False, ValueError('Missing at least one timestamp created_at/updated_at.'))
        optional_fields = [
            'address', 'zip_code', 'city',
            'email', 'phone', 'vat_number',
            'payment_term', 'notes'
            ]
        for field in optional_fields:
            client_data[field] = client_data.get(field) or None
        client_data['is_active'] = 1
        client_data['deactivated_at'] = None
        return self.repo.insert_client(
            client_data
        )
    
    def update_client(self, client_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        if 'client_id' not in client_data or not client_data['client_id']:
            return (False, ValueError('Client id must be rpvided.'))
        if 'name' not in client_data or not client_data['name']:
            return (False, ValueError('Client name is required.'))
        if 'country' not in client_data or not client_data['country']:
            return (False, ValueError('Country is required.'))
        if len(client_data['country']) != 2:
            return (False, ValueError('Country must be two letters according to WIPO standard.'))
        if ('updated_at' not in client_data or client_data['updated_at']):
            return (False, ValueError('Missing timestamp updated_at.'))
        optional_fields = [
            'address', 'zip_code', 'city',
            'email', 'phone', 'vat_number',
            'payment_term', 'notes'
            ]
        for field in optional_fields:
            client_data[field] = client_data.get(field) or None
        client_data['is_active'] = 1
        client_data['deactivated_at'] = None
        return self.repo.update_client(
            client_data
        )
    
    def deactivate_client(self, client_data:dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        if 'client_id' not in client_data or not client_data['client_id']:
            return (False, ValueError('Client id must be rpvided.'))
        if ('deactivated_at' not in client_data or client_data['deactivated_at']):
            return (False, ValueError('Missing timestamp deactivated_at.'))
   