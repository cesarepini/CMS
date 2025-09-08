# gui/windows/cases_window.py
import streamlit as st
import pandas as pd
from services.cases_service import CasesService
from services.clients_service import ClientsService
import datetime

class CasesWindow:
    def __init__(self, cases_service: CasesService, clients_service: ClientsService):
        self.cases_service = cases_service
        self.clients_service = clients_service
        # Session state for editing a case
        if 'editing_case_id' not in st.session_state:
            st.session_state.editing_case_id = None

    def render(self):
        st.title('📁 Cases Management')
        
        tab_view, tab_add = st.tabs(['📋 View Open Cases', '➕ Add New Case'])

        with tab_view:
            self._render_view_cases_tab()

        with tab_add:
            self._render_add_case_form()

    def _render_view_cases_tab(self):
        st.subheader('Active Case List')

        if st.session_state.editing_case_id is not None:
            self._render_update_case_form()

        success, cases = self.cases_service.get_open_cases()

        if not success:
            st.error(f"Failed to load cases: {cases}")
            return
        
        if not cases:
            st.info("No open cases found. You can add one in the 'Add New Case' tab.")
            return

        for case in cases:
            col1, col2, col3, col4 = st.columns([5, 3, 2, 2])
            with col1:
                st.markdown(f"**{case.get('title', 'No Title')}**")
                st.caption(f"Client Ref: {case['client_ref']}")
            with col2:
                st.write(f"Jurisdiction: {case.get('jurisdiction', 'N/A')}")
                st.caption(f"Status: {case.get('status', 'N/A')}")
            with col3:
                if st.button('✏️ Edit', key=f"edit_case_{case['case_id']}"):
                    st.session_state.editing_case_id = case['case_id']
                    st.rerun()
            with col4:
                if st.button('❌ Close Case', key=f"close_case_{case['case_id']}"):
                    close_success, msg = self.cases_service.close_case(case['case_id'])
                    if close_success:
                        st.success(f"Case '{case['client_ref']}' closed.")
                        st.rerun()
                    else:
                        st.error(msg)
            st.divider()

    def _render_add_case_form(self):
        with st.form("add_case_form", clear_on_submit=True):
            st.subheader("Add a New Case")
            
            # --- Client Selection Dropdown ---
            success, clients = self.clients_service.get_active_clients()
            if not success:
                st.error("Could not load clients for selection.")
                return
            
            # Create a list of client names for the selectbox, and a dictionary to map names back to IDs
            client_names = {client['name']: client['client_id'] for client in clients}
            selected_client_name = st.selectbox("Select a Client*", options=client_names.keys())
            title = st.text_input("Title")

            # --- Case Fields ---
            col1, col2, col3 = st.columns(3)
            with col1:
                client_ref = st.text_input("Client Reference*", help="The client's internal reference for this case.")
            with col2:
                case_type = st.selectbox("Case Type", options=['KA','DV', 'SM'], index=0)
                procedure_type = st.selectbox('Procedure Type', options=['prosecution', 'opposition', 'general counselling'], index=0)
                ipr_type = st.selectbox('IPR Type', options=['PAT', 'TM', 'DES', 'UM'], index=0)
            with col3:
                jurisdiction = st.text_input("Jurisdiction", max_chars=2, help="2-letter country code.")
                filing_number = st.text_input("Filing Number")
                filing_date = st.date_input("Filing Date", value=None)
                status = st.selectbox("Status", options=['','filed', 'pending', 'granted', 'refused', 'withdrawn', 'expired'], index=0)
            notes = st.text_area('Notes', height='content')

            submitted = st.form_submit_button("Add Case")
            if submitted:
                if not selected_client_name or not client_ref:
                    st.warning("Please select a client and provide a client reference.")
                else:
                    case_data = {
                        'case_type': case_type if case_type else None,
                        'procedure_type':procedure_type if procedure_type else None,
                        'ipr_type': ipr_type if ipr_type else None,
                        'client_id': client_names[selected_client_name],
                        'client_ref': client_ref,
                        'title': title if title else None,
                        'jurisdiction': jurisdiction.upper() if jurisdiction else None,
                        'status': status,
                        'filing_number': filing_number if filing_number else None,
                        'filing_date': filing_date.strftime('%Y-%m-%d') if filing_date else None,
                        'notes': notes if notes else None
                    }
                    add_success, result = self.cases_service.insert_case(case_data)
                    if add_success:
                        st.success("Case added successfully!")
                    else:
                        st.error(f"Error: {result}")
    
    def _render_update_case_form(self):
        st.subheader("✏️ Edit Case Details")
        success, case_data = self.cases_service.get_case_by_id(st.session_state.editing_case_id)
        if not success:
            st.error(f"Could not fetch case data: {case_data}")
            return

        with st.form("update_case_form"):
            # Client selection - slightly more complex to pre-select the correct client
            cl_success, clients = self.clients_service.get_active_clients()
            client_names = {client['name']: client['client_id'] for client in clients}
            client_ids = {client['client_id']: client['name'] for client in clients}
            
            current_client_name = client_ids.get(case_data.get('client_id'))
            client_name_list = list(client_names.keys())
            current_index = client_name_list.index(current_client_name) if current_client_name in client_name_list else 0
            
            selected_client_name = st.selectbox("Select a Client*", options=client_name_list, index=current_index)
            title = st.text_input("Title", value=case_data.get('title'))
            
            # Form fields pre-populated with existing data
            status_options = ['', 'filed', 'pending', 'granted', 'refused', 'withdrawn', 'expired']
            case_options = ['KA','DV', 'SM']
            procedure_options = ['prosecution', 'opposition', 'general counselling']
            ipr_options = ['PAT', 'TM', 'DES', 'UM']
            current_status_index = status_options.index(case_data.get('status')) if case_data.get('status') in status_options else 0
            current_case_type_index = case_options.index(case_data.get('case_type')) if case_data.get('case_type') in case_options else 0
            current_procedure_type_index = procedure_options.index(case_data.get('procedure_type')) if case_data.get('procedure_type') in procedure_options else 0
            current_case_ipr_type_index = ipr_options.index(case_data.get('ipr_type')) if case_data.get('ipr_type') in ipr_options else 0
            filing_date_val = datetime.datetime.strptime(case_data.get('filing_date'), '%Y-%m-%d').date() if case_data.get('filing_date') else None

            col1, col2, col3 = st.columns(3)
            with col1:
                client_ref = st.text_input("Client Reference*", help="The client's internal reference for this case.", value=case_data.get('client_ref'))
            with col2:
                case_type = st.selectbox("Case Type", options=case_options, index=current_case_type_index)
                procedure_type = st.selectbox('Procedure Type', options=procedure_options, index=current_procedure_type_index)
                ipr_type = st.selectbox('IPR Type', options=ipr_options, index=current_case_ipr_type_index)
            with col3:
                jurisdiction = st.text_input("Jurisdiction", max_chars=2, help="2-letter country code.", value=case_data.get('jurisdiction'))
                filing_number = st.text_input("Filing Number", value=case_data.get('filing_number', ''))
                filing_date = st.date_input("Filing Date", value=filing_date_val)
                status = st.selectbox("Status", options=status_options, index=current_status_index)
            notes = st.text_area('Notes', height='content', value=case_data.get('client_ref', ''))
            
            # Form submission buttons
            col_update, col_cancel = st.columns(2)
            with col_update:
                if st.form_submit_button("Save Changes", use_container_width=True):
                    updated_data = {
                        'case_id': st.session_state.editing_case_id,
                        'case_type': case_type if case_type else None,
                        'procedure_type':procedure_type if procedure_type else None,
                        'ipr_type': ipr_type if ipr_type else None,
                        'client_id': client_names[selected_client_name],
                        'client_ref': client_ref,
                        'title': title if title else None,
                        'jurisdiction': jurisdiction.upper() if jurisdiction else None,
                        'status': status,
                        'filing_number': filing_number if filing_number else None,
                        'filing_date': filing_date.strftime('%Y-%m-%d') if filing_date else None,
                        'notes': notes if notes else None
                    }
                    upd_success, result = self.cases_service.update_case(updated_data)
                    if upd_success:
                        st.success("Case updated successfully!")
                        st.session_state.editing_case_id = None
                        st.rerun()
                    else:
                        st.error(f"Update failed: {result}")
            with col_cancel:
                if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                    st.session_state.editing_case_id = None
                    st.rerun()