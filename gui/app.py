# gui/app.py
import streamlit as st

from gui.create_services import create_services

from gui.windows.clients_window import ClientsWindow
from gui.windows.cases_window import CasesWindow
from gui.windows.deadlines_window import DeadlinesWindow

class PatentCaseManagementApp:
    def __init__(self):
        # Use the helper function to create all our backend services
        clients_service, cases_service, deadlines_service = create_services()
        
        # Create an instance of each "window", passing the required service to it
        self.clients_window = ClientsWindow(clients_service, cases_service)
        self.cases_window = CasesWindow(cases_service, clients_service)
        self.deadlines_window = DeadlinesWindow(deadlines_service)

    def run(self):
        # Configure the page to use a wide layout for more space
        st.set_page_config(page_title='Patent Case Manager', layout='wide')

        # Initialize session state for page navigation if it doesn't exist
        if 'page' not in st.session_state:
            st.session_state.page = 'Home'
        
        # Create the main navigation in the sidebar
        st.sidebar.radio('Go to', ['Home', 'Clients', 'Cases', 'Deadlines'], key='page')

        # This is the routing logic. Based on the selection, call the 'render' method of the correct window instance.
        if st.session_state.page == 'Home':
            st.title('🏠 Welcome to the Patent Case Manager')
            st.write('Select a section from the navigation sidebar to begin.')
        elif st.session_state.page == 'Clients':
            self.clients_window.render()
        elif st.session_state.page == 'Cases':
            self.cases_window.render() # We will implement this later
        elif st.session_state.page == 'Deadlines':
            # self.deadlines_window.render() # We will implement this later
            st.info("The 'Deadlines' section is under construction.")