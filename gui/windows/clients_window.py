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
        # Initialize session_state for managing which client is being edited
        if 'editing_client_id' not in st.session_state:
            st.session_state.editing_client_id = None
        if 'viewing_cases_for_client_id' not in st.session_state:
            st.session_state.viewing_cases_for_client_id = None

    def render(self):
        st.title('👤 Clients Management')

        if st.session_state.viewing_cases_for_client_id is not None:
            self._render_client_cases_view()
            return

        inport_action = st.button("Inport Clients")
        if inport_action:
            file = st.file_uploader(
                "Choose a clients CSV file", 
                type="csv", 
                key="clients_uploader"
            )
            if file is not None:
                try:
                    # To read the file content, we decode it from bytes to a string
                    string_data = file.getvalue().decode("utf-8")
                    # We use io.StringIO to treat the string as a file for the csv reader
                    string_io = io.StringIO(string_data)
                    
                    reader = csv.DictReader(string_io)
                    
                    # We use an expander to show the data before importing
                    with st.expander("Preview CSV Data"):
                        st.dataframe(pd.read_csv(file))

                    if st.button("Import these clients"):
                        with st.spinner("Importing..."):
                            for row in reader:
                                success, result = self.clients_service.insert_client(row)
                                if success:
                                    st.success(f"Successfully imported client: {row.get('name')}")
                                else:
                                    st.error(f"Failed to import client {row.get('name')}: {result}")
                        st.rerun() # Refresh the app to show new clients

                except Exception as e:
                    st.error(f"An error occurred while processing the file: {e}")

        else:
            tab_view, tab_add = st.tabs(['📋 View Clients', '➕ Add New Client'])

            with tab_view:
                self._render_view_clients_tab()
            with tab_add:
                st.subheader("Add new client")
                self._render_add_client_form()

    def _render_view_clients_tab(self):
        st.subheader('Active Client List')

        # If we are in edit mode, render the update form
        if st.session_state.editing_client_id is not None:
            self._render_update_client_form()

        # Fetch and display all active clients
        success, clients = self.clients_service.get_active_clients()

        if not success:
            st.error(f"Failed to load clients: {clients}")
            return
        
        if not clients:
            st.info("No active clients found. You can add one in the 'Add New Client' tab.")
            return

        # Display clients with interactive buttons
        for client in clients:
            col1, col2, col3, col4, col5 = st.columns([4, 4, 2, 1, 1])
            with col1:
                st.markdown(f"**{client['name']}** (`{client['client_id']} - {client['client_code']}`)")
            with col2:
                st.write(f'{client.get('address', '')} , {client.get('zip_code')} {client.get('city', '')}')
                st.write(f"Country: {client.get('country')}")
                st.write(f'{client.get('phone', 'No phone')}, {client.get('email', 'No e-mail')}')
                st.write(client.get('vat_number', ''))
            with col3:
                if st.button('✏️ Edit', key=f"edit_{client['client_id']}"):
                    st.session_state.editing_client_id = client['client_id']
                    st.rerun()
                     # Update button sets the session state to the client's ID and reruns
                if st.button('📁 View Cases', key=f"cases_{client['client_id']}"):
                    st.session_state.viewing_cases_for_client_id = client['client_id']
                    st.rerun()
                if st.button('🗑️ Deactivate', key=f"deact_{client['client_id']}"):
                    deact_success, msg = self.clients_service.deactivate_client(client['client_id'])
                    if deact_success:
                        st.success(f"Client '{client['name']}' deactivated.")
                        st.rerun()
                    else:
                        st.error(msg)
            st.divider()

    def _render_client_cases_view(self):
        client_id = st.session_state.viewing_cases_for_client_id
        cl_success, client_data = self.clients_service.get_client_by_id(client_id)
        client_name = client_data['name'] if cl_success else 'Selected Client'
        
        st.subheader(f"📁 Open Cases for: {client_name}")

        # Fetch and display the cases
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
                    # This button sets the state for BOTH editing and navigation
                    if st.button("▶️ Go to Case", key=f"goto_case_{case['case_id']}"):
                        st.session_state.editing_case_id = case['case_id']
                        st.session_state.page = 'Cases'
                        st.rerun()
                st.markdown("---")

        # Button to go back to the main client list
        if st.button("⬅️ Back to Client List"):
            st.session_state.viewing_cases_for_client_id = None
            st.rerun()
    
    def _render_add_client_form(self):
        with st.form("add_client_form", clear_on_submit=True):
            st.subheader("Add a New Client")
            # Get required fields based on the database schema
            name = st.text_input("Client Name*", help="Full name of the client.")
            client_code = st.text_input("Client Code*", max_chars=3, help="A unique 3-letter code.")
            address = st.text_input("Address")
            zip_code = st.text_input("ZIP Code")
            city = st.text_input("City")
            country = st.text_input("Country Code*", max_chars=2, help="2-letter ISO country code.")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            vat_number = st.text_input("VAT Number")
            payment_term = st.number_input("Payment term", min_value=0, value=14)
            notes = st.text_area("Notes", height="content")
            
            submitted = st.form_submit_button("Add Client")
            if submitted:
                # Basic validation
                if not name or not client_code or not country:
                    st.warning("Please fill in all required fields (*).")
                else:
                    client_data = {
                        'name': name,
                        'client_code': client_code.upper(),
                        'address': address,
                        'zip_code':zip_code,
                        'city': city,
                        'country': country.upper(),
                        'email': email,
                        'phone': phone,
                        'vat_number': vat_number,
                        'payment_term': payment_term,
                        'notes': notes,
                    }
                    success, result = self.clients_service.insert_client(client_data)
                    if success:
                        st.success("Client added successfully!")
                    else:
                        st.error(f"Error: {result}")

    def _render_update_client_form(self):
        st.subheader("✏️ Edit Client Details")
        # Get the full data for the client being edited
        success, client_data = self.clients_service.get_client_by_id(st.session_state.editing_client_id)
        
        if not success:
            st.error(f"Could not fetch client data: {client_data}")
            return

        with st.form("update_client_form"):
            name = st.text_input("Client Name*", value=client_data.get('name'))
            client_code = st.text_input("Client Code*", value=client_data.get('client_code'), max_chars=3)
            address = st.text_input("Address", value=client_data.get('address'))
            zip_code = st.text_input("ZIP Code", value=client_data.get('zip_code'))
            city = st.text_input("City", value=client_data.get('city'))
            country = st.text_input("Country Code*", value=client_data.get('country'), max_chars=2)
            email = st.text_input("Email", value=client_data.get('email'))
            phone = st.text_input("Phone", value=client_data.get('phone'))
            vat_number = st.text_input("VAT Number", value=client_data.get('vat_number'))
            payment_term = st.number_input("Payment term", min_value=0, value=client_data.get('payment_term'))
            notes = st.text_area("Notes", height="content", value=client_data.get('notes'))
            
            col_update, col_cancel = st.columns(2)
            with col_update:
                if st.form_submit_button("Save Changes", use_container_width=True):
                    updated_data = {
                        'client_id': st.session_state.editing_client_id,
                        'name': name,
                        'client_code': client_code.upper(),
                        'address': address,
                        'zip_code':zip_code,
                        'city': city,
                        'country': country.upper(),
                        'email': email,
                        'phone': phone,
                        'vat_number': vat_number,
                        'payment_term': payment_term,
                        'notes': notes
                    }
                    upd_success, result = self.clients_service.update_client(updated_data)
                    if upd_success:
                        st.success("Client updated successfully!")
                        st.session_state.editing_client_id = None
                        st.rerun()
                    else:
                        st.error(f"Update failed: {result}")

            with col_cancel:
                if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                    st.session_state.editing_client_id = None
                    st.rerun()