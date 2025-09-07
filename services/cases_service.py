from datetime import datetime
from typing import Tuple, Union, List, Dict

from repos.cases_repo import CasesRepo
from repos.deadlines_repo import DeadlinesRepo

class CasesService():
    def __init__(self, cases_repo:CasesRepo, deadlines_repo:DeadlinesRepo):
        self.cases_repo = cases_repo
        self.deadlines_repo = deadlines_repo

    def _is_valid_date(self, date_string: str) -> bool:
        """Checks if a string is a valid YYYY-MM-DD date."""
        if not date_string:
            return True # Allow empty/None dates
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
        
    def _validate_case_data(self, case_data: dict) -> List[str]:
        """Validates case data, returning a list of error messages."""
        errors = []
        if not case_data.get('client_id'):
            errors.append('Client ID is required.')
        if not case_data.get('client_ref'):
            errors.append('Client ref is required.')
        if case_data.get('jurisdiction') and len(case_data['jurisdiction']) != 2:
            errors.append('Jurisdiction must be two letters according to WIPO standard.')
        if not self._is_valid_date(case_data.get('filing_date')):
            errors.append('Filing date must be in YYYY-MM-DD format.')
        return errors

    def get_all_cases(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.cases_repo.get_all_cases()
    
    def get_open_cases(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.cases_repo.get_open_cases()
    
    def get_cases_by_client(self, client_id:int) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.cases_repo.get_cases_by_client(client_id)
    
    def get_open_cases_by_client(self, client_id:int) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.cases_repo.get_open_cases_by_client(client_id)
    
    def get_cases_by_jurisdiction(self, jurisdiction:str) -> Tuple[bool, Union[List[Dict], Exception]]:
        if len(jurisdiction) != 2:
            return (False, ValueError('Jurisdiction must have 2 letters.'))
        return self.cases_repo.get_cases_by_jurisdiction(jurisdiction)
    
    def get_cases_by_procedure(self, procedure:str) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.cases_repo.get_cases_by_procedure(procedure)
    
    def get_cases_by_ipr_type(self, ipr_type:str) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.cases_repo.get_cases_by_ipr_type(ipr_type)

    def get_cases_by_status(self, status:str) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.cases_repo.get_cases_by_status(status)
    
    def get_case_by_id(self, case_id: int) -> Tuple[bool, Union[Dict, None, Exception]]:
        return self.cases_repo.get_case_by_id(case_id, 'case_id')
    
    def insert_case(self, case_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        errors = self._validate_case_data(case_data)
        if errors:
            return (False, ValueError('/'.join(errors)))
        optional_fields = [
            'case_type', 'procedure_type', 'ipr_type',
            'title', 'jurisdiction', 'filing_date',
            'filing_number', 'status', 'notes'
            ]
        for field in optional_fields:
            case_data[field] = case_data.get(field) or None
        case_data['is_open'] = 1
        case_data['closed_at'] = None
        case_data['created_at'] = case_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.cases_repo.insert_case(
            case_data
        )
    
    def update_case(self, case_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        if 'case_id' not in case_data or not case_data['case_id']:
            return (False, ValueError('Case ID is required.'))
        errors = self._validate_case_data(case_data)
        if errors:
            return (False, ValueError('/'.join(errors)))
        optional_fields = [
            'case_type', 'procedure_type', 'ipr_type',
            'title', 'jurisdiction', 'filing_date',
            'filing_number', 'status', 'notes'
            ]
        for field in optional_fields:
            case_data[field] = case_data.get(field) or None
        case_data['is_open'] = 1
        case_data['closed_at'] = None
        case_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        case_id = case_data.pop('case_id')
        return self.cases_repo.update_case(case_data, case_id)
    
    def close_case(self, case_id: int) -> Tuple[bool, Union[int, str, Exception]]:
        success, open_deadlines = self.deadlines_repo.get_open_deadlines_by_case(case_id)
        if not success:
            return False, open_deadlines
        if open_deadlines and len(open_deadlines) > 0:
            return False, 'Case has open deadlines and cannot be closed.'

        return self.cases_repo.close_case(case_id)