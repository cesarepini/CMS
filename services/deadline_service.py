from datetime import datetime
from typing import Tuple, Union, List, Dict

from repos.deadlines_repo import DeadlinesRepo

class DeadlineService():
    def __init__(self, deadlines_repo:DeadlinesRepo):
        self.deadlines_repo = deadlines_repo

    def get_all_deadlines(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.deadlines_repo.get_all_deadlines()
    
    def get_open_deadlines(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.deadlines_repo.get_open_deadlines()
    
    def get_open_deadlines_by_case(self, case_id:int) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.deadlines_repo.get_open_deadlines_by_case(case_id)
    
    def get_deadline_by_id(self, deadline_id: int) -> Tuple[bool, Union[Dict, None, Exception]]:
        return self.deadlines_repo.get_deadline_by_id(deadline_id, 'deadline_id')
    
    def insert_deadline(self, deadline_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        mandatory_fields = [
            'case_id',
            'description',
            'due_date',
            'deadline_type',
            'status'
        ]
        for field in mandatory_fields:
            if field not in deadline_data or not deadline_data[field]:
                return False, ValueError(f'{field} is required')
        if not bool(datetime.strptime(deadline_data['due_date'], '%d-%m-%Y')):
            return(False, 'Incorrect due date.')
        deadline_data['completed'] = 0
        deadline_data['created_at'] = deadline_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deadline_data['completed_at'] = None
        return self.deadlines_repo.insert_deadline(deadline_data)
    
    def update_deadline(self, deadline_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        mandatory_fields = [
            'deadline_id',
            'case_id',
            'description',
            'due_date',
            'deadline_type',
            'status'
        ]
        for field in mandatory_fields:
            if field not in deadline_data or not deadline_data[field]:
                return False, ValueError(f'{field} is required')
        try:
            bool(datetime.strptime(deadline_data['due_date'], '%d-%m-%Y'))
        except ValueError:
            return(False, 'Incorrect due date.')
        deadline_data['completed'] = 0
        deadline_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deadline_data['completed_at'] = None
        deadline_id = deadline_data.pop('deadline_id')
        return self.deadlines_repo.update_deadline(deadline_data, deadline_id)
    
    def mark_deadline_completed(self, deadline_id: int) -> Tuple[bool, Union[int, str, Exception]]:
        return self.deadlines_repo.mark_deadline_completed(deadline_id)