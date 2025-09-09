# gui/windows/clients_window.py
import csv
import io
import streamlit as st
import pandas as pd
from services.clients_service import ClientsService
from services.cases_service import CasesService

class ClientsWindow:
    def __init__(self, clients_service: ClientsService, cases_service:CasesService):
        self.clients_service = clients_service
        self.cases_service = cases_service
        if 'editing_client_id' not in st.session_state:
            st.session_state.editing_client_id = None
        if 'viewing_cases_for_client_id' not in st.session_state:
            st.session_state.viewing_cases_for_client_id = None

    def render(self):
        st.title('👤 Clients Management')

        if st.session_state.viewing_cases_for_client_id is not None:
            self._render_client_cases_view()
            return

        tab_view, tab_add = st.tabs(['📋 View Clients', '➕ Add New Client'])

        with tab_view:
            self._render_view_clients_tab()
        with tab_add:
            st.subheader("Add a Single Client")
            self._render_add_client_form()
            st.divider()
            st.subheader("Or Import Clients from CSV")
            self._render_batch_import_clients()

    def _render_batch_import_clients(self):
        uploaded_file = st.file_uploader(
            "Choose a clients CSV file", 
            type="csv", 
            key="clients_uploader"
        )

        if uploaded_file is not None:
            # The button's logic is now handled by the 'on_click' callback.
            st.button(
                "Confirm and Import Clients", 
                on_click=self._handle_client_import, 
                args=(uploaded_file,)
            )

    def _handle_client_import(self, uploaded_file):
        # This function is the callback. It runs safely between reruns.
        try:
            with st.spinner("Importing..."):
                string_data = uploaded_file.getvalue().decode("utf-8")
                string_io = io.StringIO(string_data)
                reader = csv.DictReader(string_io)
                rows_to_import = list(reader)
                
                success_count = 0
                for row in rows_to_import:
                    success, result = self.clients_service.insert_client(row)
                    if success:
                        success_count += 1
                    else:
                        st.error(f"Failed to import client '{row.get('name', 'N/A')}': {result}")
                
                st.success(f"Import complete! {success_count} of {len(rows_to_import)} clients imported successfully.")
                
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
        
        # This line is now safe because it's inside the callback.
        st.session_state.clients_uploader = None

    def _render_view_clients_tab(self):
        st.subheader('Active Client List')
        if st.session_state.editing_client_id is not None:
            self._render_update_client_form()

        success, clients = self.clients_service.get_active_clients()
        if not success:
            st.error(f"Failed to load clients: {clients}")
            return
        if not clients:
            st.info("No active clients found.")
            return

        for client in clients:
            col1, col2, col3, col4, col5 = st.columns([4, 4, 2, 1, 1])
            with col1:
                st.markdown(f"**{client['name']}** (`{client['client_id']} - {client['client_code']}`)")
            with col2:
                st.write(f"{client.get('address', '')}, {client.get('zip_code')} {client.get('city', '')}")
                st.write(f"Country: {client.get('country')}")
            with col3:
                if st.button('✏️ Edit', key=f"edit_{client['client_id']}"):
                    st.session_state.editing_client_id = client['client_id']
                    st.rerun()
                if st.button('📁 View Cases', key=f"cases_{client['client_id']}"):
                    st.session_state.viewing_cases_for_client_id = client['client_id']
                    st.rerun()
            with col5: # Adjusted column for better spacing
                if st.button('🗑️ Deactivate', key=f"deact_{client['client_id']}"):
                    deact_success, msg = self.clients_service.deactivate_client(client['client_id'])
                    if deact_success:
                        st.success(f"Client '{client['name']}' deactivated.")
                        st.rerun()
                    else:
                        st.error(msg)
            st.divider()

    def _render_client_cases_view(self):
        # ... logic for viewing cases ...
        client_id = st.session_state.viewing_cases_for_client_id
        cl_success, client_data = self.clients_service.get_client_by_id(client_id)
        client_name = client_data['name'] if cl_success else 'Selected Client'
        st.subheader(f"📁 Open Cases for: {client_name}")
        case_success, cases = self.cases_service.get_open_cases_by_client(client_id)
        if not case_success:
            st.error(f"Could not load cases: {cases}")
        elif not cases:
            st.info("This client has no open cases.")
        else:
            for case in cases:
                col1, col2, col3 = st.columns([5, 3, 2])
                with col1:
                    st.markdown(f"**{case.get('title', 'No Title')}**")
                    st.caption(f"Ref: {case.get('client_ref')}")
                with col2:
                    st.markdown(f"Jurisdiction: **{case.get('jurisdiction', 'N/A')}**")
                    st.caption(f"Status: {case.get('status', 'N/A')}")
                with col3:
                    if st.button("▶️ Go to Case", key=f"goto_case_{case['case_id']}"):
                        st.session_state.editing_case_id = case['case_id']
                        st.session_state.page = 'Cases'
                        st.rerun()
                st.markdown("---")
        if st.button("⬅️ Back to Client List"):
            st.session_state.viewing_cases_for_client_id = None
            st.rerun()
    
    def _render_add_client_form(self):
        # ... logic for add form ...
        with st.form("add_client_form", clear_on_submit=True):
            st.subheader("Add a New Client")
            name = st.text_input("Client Name*")
            client_code = st.text_input("Client Code*", max_chars=3)
            # ... other fields
            country = st.text_input("Country Code*", max_chars=2)
            submitted = st.form_submit_button("Add Client")
            if submitted:
                client_data = {'name': name, 'client_code': client_code, 'country': country} # simplified for brevity
                success, result = self.clients_service.insert_client(client_data)
                if success: st.success("Client added successfully!")
                else: st.error(f"Error: {result}")

    def _render_update_client_form(self):
        # ... logic for update form ...
        st.subheader("✏️ Edit Client Details")
        success, client_data = self.clients_service.get_client_by_id(st.session_state.editing_client_id)
        if not success:
            st.error(f"Could not fetch client data: {client_data}")
            return
        with st.form("update_client_form"):
            name = st.text_input("Client Name*", value=client_data.get('name'))
            # ... other fields
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                updated_data = {'client_id': st.session_state.editing_client_id, 'name': name} # simplified for brevity
                upd_success, result = self.clients_service.update_client(updated_data)
                if upd_success:
                    st.success("Client updated successfully!")
                    st.session_state.editing_client_id = None
                    st.rerun()
                else:
                    st.error(f"Update failed: {result}")