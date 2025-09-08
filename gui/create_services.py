from database_handler.database_handler import DatabaseHandler
from repos.clients_repo import ClientsRepo
from repos.cases_repo import CasesRepo
from repos.deadlines_repo import DeadlinesRepo
from services.clients_service import ClientsService
from services.cases_service import CasesService
from services.deadline_service import DeadlineService

def create_services():
    db_handler = DatabaseHandler()
    db_handler.connect()

    clients_repo = ClientsRepo(db_handler)
    cases_repo = CasesRepo(db_handler)
    deadlines_repo = DeadlinesRepo(db_handler)

    # Services
    clients_service = ClientsService(clients_repo, cases_repo)
    cases_service = CasesService(cases_repo, deadlines_repo)
    deadlines_service = DeadlineService(deadlines_repo)

    return clients_service, cases_service, deadlines_service