# gui/windows/deadlines_window.py
import streamlit as st
from services.deadline_service import DeadlineService
from services.cases_service import CasesService
from services.clients_service import ClientsService
import datetime

class DeadlinesWindow:
    def __init__(self, deadline_service: DeadlineService, cases_service: CasesService, clients_service: ClientsService):
        self.deadline_service = deadline_service
        self.cases_service = cases_service
        self.clients_service = clients_service

        # Initialize session state for editing
        if 'editing_deadline_id' not in st.session_state:
            st.session_state.editing_deadline_id = None

    def render(self):
        st.title('📅 Deadlines Management')

        tab_view, tab_add = st.tabs(['📋 View Open Deadlines', '➕ Add New Deadline'])

        with tab_view:
            self._render_view_deadlines_tab()

        with tab_add:
            self._render_add_deadline_form()

    def _render_view_deadlines_tab(self):
        st.subheader("Upcoming and Overdue Deadlines")

        # --- NEW --- Show the update form if we are in edit mode
        if st.session_state.editing_deadline_id is not None:
            self._render_update_deadline_form()

        success, deadlines = self.deadline_service.get_open_deadlines()

        if not success:
            st.error(f"Failed to load deadlines: {deadlines}")
            return
        
        if not deadlines:
            st.info("No open deadlines found. You can add one in the 'Add New Deadline' tab.")
            return

        for deadline in deadlines:
            case_success, case = self.cases_service.get_case_by_id(deadline['case_id'])
            client_success, client = self.clients_service.get_client_by_id(case['client_id']) if case_success else (False, None)
            
            client_name = client['name'] if client_success else "Unknown Client"
            case_ref = case['client_ref'] if case_success else "Unknown Case"

            col1, col2, col3, col4 = st.columns([4, 3, 1, 2]) # Added a column for Edit button
            with col1:
                st.markdown(f"**{deadline['description']}**")
                st.caption(f"Due: {deadline['due_date']}")
            with col2:
                st.write(f"Client: {client_name}")
                st.caption(f"Case Ref: {case_ref}")
            with col3:
                # --- NEW --- Edit button
                if st.button('✏️ Edit', key=f"edit_{deadline['deadline_id']}"):
                    st.session_state.editing_deadline_id = deadline['deadline_id']
                    st.rerun()
            with col4:
                if st.button('✅ Mark as Done', key=f"done_{deadline['deadline_id']}", use_container_width=True):
                    done_success, result = self.deadline_service.mark_deadline_completed(deadline['deadline_id'])
                    if done_success:
                        st.success("Deadline marked as complete!")
                        st.rerun()
                    else:
                        st.error(f"Failed to complete deadline: {result}")

            st.divider()

    def _render_add_deadline_form(self):
        st.subheader("Add a New Deadline")
        case_success, cases = self.cases_service.get_open_cases()
        if not case_success:
            st.error("Could not load open cases for selection.")
            return
        if not cases:
            st.warning("There are no open cases. Please add a case before adding a deadline.")
            return
        case_options = {}
        for case in cases:
            client_success, client = self.clients_service.get_client_by_id(case['client_id'])
            client_name = client['name'] if client_success else "Unknown"
            option_label = f"{client_name} - {case['client_ref']} ({case.get('title', 'No Title')})"
            case_options[option_label] = case['case_id']

        with st.form("add_deadline_form", clear_on_submit=True):
            selected_case_label = st.selectbox("Select a Case*", options=case_options.keys())
            description = st.text_area("Description*")
            due_date = st.date_input("Due Date*", min_value=datetime.date.today())
            deadline_type = st.selectbox("Deadline Type", options=['statutory', 'client', 'internal'], index=0)
            
            submitted = st.form_submit_button("Add Deadline")
            if submitted:
                if not selected_case_label or not description:
                    st.warning("Please select a case and provide a description.")
                else:
                    deadline_data = {
                        'case_id': case_options[selected_case_label],
                        'description': description,
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'deadline_type': deadline_type,
                        'status': 'Pending'
                    }
                    add_success, result = self.deadline_service.insert_deadline(deadline_data)
                    if add_success:
                        st.success("Deadline added successfully!")
                    else:
                        st.error(f"Error: {result}")

    # --- NEW METHOD ---
    def _render_update_deadline_form(self):
        st.subheader("✏️ Edit Deadline Details")
        
        deadline_id = st.session_state.editing_deadline_id
        success, deadline_data = self.deadline_service.get_deadline_by_id(deadline_id)
        if not success:
            st.error(f"Could not fetch deadline data: {deadline_data}")
            return
        
        # Prepare case options for the dropdown
        case_success, cases = self.cases_service.get_open_cases()
        case_options = {}
        for case in cases:
            client_success, client = self.clients_service.get_client_by_id(case['client_id'])
            client_name = client['name'] if client_success else "Unknown"
            option_label = f"{client_name} - {case['client_ref']} ({case.get('title', 'No Title')})"
            case_options[option_label] = case['case_id']
        
        # Find the index of the currently selected case to pre-fill the dropdown
        case_id_to_label = {v: k for k, v in case_options.items()}
        current_case_label = case_id_to_label.get(deadline_data['case_id'])
        case_labels = list(case_options.keys())
        current_case_index = case_labels.index(current_case_label) if current_case_label in case_labels else 0

        # Prepare other pre-filled values
        due_date_val = datetime.datetime.strptime(deadline_data['due_date'], '%Y-%m-%d').date()
        deadline_types = ['statutory', 'client', 'internal']
        current_type_index = deadline_types.index(deadline_data['deadline_type']) if deadline_data['deadline_type'] in deadline_types else 0

        with st.form("update_deadline_form"):
            selected_case_label = st.selectbox("Select a Case*", options=case_labels, index=current_case_index)
            description = st.text_area("Description*", value=deadline_data['description'])
            due_date = st.date_input("Due Date*", value=due_date_val, min_value=datetime.date.today())
            deadline_type = st.selectbox("Deadline Type", options=deadline_types, index=current_type_index)

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes", use_container_width=True):
                    updated_data = {
                        'deadline_id': deadline_id,
                        'case_id': case_options[selected_case_label],
                        'description': description,
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'deadline_type': deadline_type,
                        'status': 'Pending' # Keep status as pending on update
                    }
                    upd_success, result = self.deadline_service.update_deadline(updated_data)
                    if upd_success:
                        st.success("Deadline updated successfully!")
                        st.session_state.editing_deadline_id = None
                        st.rerun()
                    else:
                        st.error(f"Update failed: {result}")
            with col2:
                if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                    st.session_state.editing_deadline_id = None
                    st.rerun()