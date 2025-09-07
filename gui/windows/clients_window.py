from datetime import datetime
import streamlit as st
from services.clients_service import ClientsService
from typing import Optional


class ClientsWindow:
    def __init__(self, clients_service: ClientsService):
        self.clients_service = clients_service

    def render(self):
        st.title("👤 Clients")

        tab1, tab2 = st.tabs(["View Clients", "Add New Client"])

        with tab1:
            self._render_client_list()

        with tab2:
            self._render_add_client_form()

    def _render_client_list(self):
        st.subheader("📋 All Clients")
        success, clients = self.clients_service.get_active_clients()

        if success:
            for client in clients:
                st.markdown("---")
                cols = st.columns([3, 3, 2, 1, 1])
                cols[0].markdown(f"**{client['name']}**")
                cols[1].markdown(client.get("email", "—"))
                cols[2].markdown(client.get("country", "—"))

                if cols[3].button("✏️ Update", key=f"update_{client['client_id']}"):
                    self.editing_client = client

                if cols[4].button("🗑 Deactivate", key=f"deactivate_{client['client_id']}"):
                    success, clients = self.clients_service.deactivate_client(client["client_id"])
                    if success:
                        st.success("Client deactivated.")
                        st.rerun()
                    else:
                        st.error(str(clients))

            if hasattr(self, "editing_client") and self.editing_client:
                st.markdown("### ✏️ Update Client")
                with st.form("update_client_form"):
                    name = st.text_input("Name", value=self.editing_client["name"])
                    country = st.text_input("Country", value=self.editing_client["country"])
                    email = st.text_input("Email", value=self.editing_client.get("email", ""))

                    submitted = st.form_submit_button("Save Changes")
                    if submitted:
                        updated_data = {
                            "client_id": self.editing_client["client_id"],
                            "name": name,
                            "country": country,
                            "email": email,
                            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        success, result = self.clients_service.update_client(updated_data)
                        if success:
                            st.success("Client updated.")
                            del self.editing_client
                            st.rerun()
                        else:
                            st.error(str(result))


        if not success:
            st.error(f"Failed to load clients: {clients}")
            return

        if not clients:
            st.info("No clients found.")
            return

        st.dataframe(clients, use_container_width=True)

    def _render_add_client_form(self):
        st.subheader("➕ Add New Client")

        with st.form("add_client_form", clear_on_submit=True):
            name = st.text_input("Client Name*", max_chars=100)
            code = st.text_input("Client Code*", max_chars=3)
            country = st.text_input("Country Code (ISO-2)*", max_chars=2)

            # Optional fields
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            with col2:
                address = st.text_input("Address")
                city = st.text_input("City")
                zip_code = st.text_input("ZIP Code")

            vat_number = st.text_input("VAT Number")
            payment_term = st.number_input("Payment Term (days)", min_value=0, step=1)
            notes = st.text_area("Notes")

            submitted = st.form_submit_button("Add Client")

            if submitted:
                client_data = {
                    "name": name,
                    "client_code": code.upper(),
                    "country": country.upper(),
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "city": city,
                    "zip_code": zip_code,
                    "vat_number": vat_number,
                    "payment_term": payment_term,
                    "notes": notes
                }

                self.handle_add_client(client_data)

            #     success, response = self.clients_service.insert_client(client_data)
            #     if success:
            #         st.success("Client added successfully.")
            #         st.experimental_rerun()
            #     else:
            #         st.error(f"Error: {response}")

    def handle_add_client(self, client_data: dict):
        success, result = self.clients_service.insert_client(client_data)
        
        if success:
            st.success("Client added successfully.")
            st.rerun()
        else:
            st.error(f"Error: {result}")
