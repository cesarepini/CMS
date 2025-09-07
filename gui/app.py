import streamlit as st

from gui.create_services import create_services

from gui.windows.clients_window import ClientsWindow
from gui.windows.cases_window import CasesWindow
from gui.windows.deadlines_window import DeadlinesWindow

class PatentCaseManagementApp:
    def __init__(self):
        clients_service, cases_service, deadlines_service = create_services()
        self.clients_window = ClientsWindow(clients_service)
        self.cases_window = CasesWindow(cases_service)
        self.deadlines_window = DeadlinesWindow(deadlines_service)

    def run(self):
        st.set_page_config(page_title="Patent Case Manager", layout="wide")
        page = st.sidebar.radio("Go to", ["Clients", "Cases", "Deadlines"])

        if page == "Clients":
            self.clients_window.render()
        elif page == "Cases":
            pass
            #self.cases_window.render()
        elif page == "Deadlines":
            pass
            #self.deadlines_window.render()
