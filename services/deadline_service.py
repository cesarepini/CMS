from datetime import date, datetime
from typing import Tuple, Union, List, Dict

from repos.deadlines_repo import DeadlinesRepo

class DeadlineService():
    def __init__(self, deadlines_repo:DeadlinesRepo):
        self.deadlines_repo = deadlines_repo

    def _validate_deadline_data(self, deadline_data: dict) -> List[str]:
        """Validates deadline data, returning a list of error messages."""
        errors = []
        mandatory_fields = ['case_id', 'description', 'due_date', 'deadline_type', 'status']
        for field in mandatory_fields:
            if not deadline_data.get(field):
                errors.append(f'{field} is required.')
        
        due_date_str = deadline_data.get('due_date')
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                if due_date < date.today():
                    errors.append('Due date cannot be in the past.')
            except ValueError:
                errors.append('Due date must be in YYYY-MM-DD format.')
        
        return errors

    def get_all_deadlines(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.deadlines_repo.get_all_deadlines()
    
    def get_open_deadlines(self) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.deadlines_repo.get_open_deadlines()
    
    def get_open_deadlines_by_case(self, case_id:int) -> Tuple[bool, Union[List[Dict], Exception]]:
        return self.deadlines_repo.get_open_deadlines_by_case(case_id)
    
    def get_deadline_by_id(self, deadline_id: int) -> Tuple[bool, Union[Dict, None, Exception]]:
        return self.deadlines_repo.get_deadline_by_id(deadline_id, 'deadline_id')
    
    def insert_deadline(self, deadline_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        errors = self._validate_deadline_data(deadline_data)
        if errors:
            return False, ValueError(". ".join(errors))
        deadline_data['completed'] = 0
        deadline_data['created_at'] = deadline_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deadline_data['completed_at'] = None
        return self.deadlines_repo.insert_deadline(deadline_data)
    
    def update_deadline(self, deadline_data: dict) -> Tuple[bool, Union[Dict, None, Exception]]:
        if not deadline_data.get('deadline_id'):
            return False, ValueError('Deadline ID must be provided.')
        errors = self._validate_deadline_data(deadline_data)
        if errors:
            return False, ValueError(". ".join(errors))
        deadline_data['completed'] = 0
        deadline_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deadline_data['completed_at'] = None
        deadline_id = deadline_data.pop('deadline_id')
        return self.deadlines_repo.update_deadline(deadline_data, deadline_id)
    
    def mark_deadline_completed(self, deadline_id: int) -> Tuple[bool, Union[int, str, Exception]]:
        return self.deadlines_repo.mark_deadline_completed(deadline_id)