from datetime import datetime
from typing import Tuple, Union, List, Dict
import re

from repos.clients_repo import ClientsRepo
from repos.cases_repo import CasesRepo

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class ClientsService():
    def __init__(self, clients_repo: ClientsRepo, cases_repo:CasesRepo):
        self.clients_repo = clients_repo
        self.cases_repo = cases_repo

    def _validate_client_data(self, client_data:dict) ->List[str]:
        errors = []
        if not client_data.get('name'):
            errors.append('Client name is required.')
        if not client_data.get('country'):
            errors.append('Country is required.')
        elif len(client_data['country']) != 2:
            errors.append('Country name must have 2 letters according to WIPO standard.')
        if client_data.get('email') and not re.match(EMAIL_REGEX, client_data['email']):
            errors.append('Invalid email address format.')
        return errors

    def get_all_clients(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.clients_repo.get_all_clients()
    
    def get_active_clients(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.clients_repo.get_active_clients()
    
    def get_client_by_id(self, client_id: int) -> Tuple[bool, Union[Dict, None, Exception]]:
        return self.clients_repo.get_client_by_id(client_id, 'client_id')
    
    def insert_client(self, client_data: dict) -> Tuple[bool, Union[int, Exception]]:
        errors = self._validate_client_data(client_data)
        if errors:
            return (False, ValueError(' '.join(errors)))
        optional_fields = [
            'address', 'zip_code', 'city',
            'email', 'phone', 'vat_number',
            'payment_term', 'notes'
            ]
        for field in optional_fields:
            client_data[field] = client_data.get(field) or None
        client_data['is_active'] = 1
        client_data['deactivated_at'] = None
        client_data['created_at'] = client_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.clients_repo.insert_client(
            client_data
        )
    
    def update_client(self, client_data: dict) -> Tuple[bool, Union[int, Exception]]:
        if 'client_id' not in client_data or not client_data['client_id']:
            return (False, ValueError('Client ID must be provided.'))
        errors = self._validate_client_data(client_data)
        if errors:
            return (False, ValueError(' '.join(errors)))
        optional_fields = [
            'address', 'zip_code', 'city',
            'email', 'phone', 'vat_number',
            'payment_term', 'notes'
            ]
        for field in optional_fields:
            client_data[field] = client_data.get(field) or None
        client_data['is_active'] = 1
        client_data['deactivated_at'] = None
        client_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_id = client_data.pop('client_id')
        return self.clients_repo.update_client(client_data, client_id)
    
    def deactivate_client(self, client_id: int) -> Tuple[bool, Union[int, Exception]]:
        success, open_cases = self.cases_repo.get_open_cases_by_client(client_id)
        if not success:
            return False, open_cases
        if open_cases and len(open_cases) > 0:
            return False, 'Client has open cases and cannot be deactivated.'

        return self.clients_repo.deactivate_client(client_id)