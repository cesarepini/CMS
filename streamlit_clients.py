import streamlit as st
import pandas as pd
from services.clients_service import ClientService
from repos.clients_repo import ClientsRepo

from database_handler.database_handler import DatabaseHandler

st.title("Client Manager")

# Initialize service
db = DatabaseHandler()
repo = ClientsRepo(db)
client_service = ClientService(repo)

st.header("Active Clients")

# Fetch active clients
ok, result = client_service.get_active_clients()

if not ok:
    st.error(f"Error fetching clients: {result}")
else:
    st.success(f"Found {len(result)} clients")

    # Convert to DataFrame for display
    df = pd.DataFrame(result)

    # Display table
    st.dataframe(df, use_container_width=True)
