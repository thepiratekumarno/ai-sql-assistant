import streamlit as st
from src.database.schema import get_databases, get_tables
from src.database.connection import test_connection
from src.utils.helpers import get_column_types

def show_setup_ui():
    """Show credential setup UI"""
    st.title("🔐 Setup Your Environment")
    
    # Google API Key
    google_api_key = st.text_input("Google API Key", type="password")
    
    # MySQL Credentials
    st.subheader("MySQL Database Credentials")
    col1, col2 = st.columns(2)
    with col1:
        mysql_host = st.text_input("Host", "localhost")
        mysql_user = st.text_input("Username", "root")
    with col2:
        mysql_port = st.number_input("Port", 3306)
        mysql_password = st.text_input("Password", type="password")
    
    credentials = {
        "host": mysql_host,
        "user": mysql_user,
        "password": mysql_password,
        "port": mysql_port
    }
    
    # Test connection button
    if st.button("Test Connection"):
        if test_connection(credentials):
            st.success("✅ Connection successful!")
            databases = get_databases(credentials)
            st.session_state.databases = databases
            st.session_state.mysql_creds = credentials
        else:
            st.error("❌ Connection failed")
    
    # Final setup
    if st.button("Complete Setup"):
        if google_api_key and 'mysql_creds' in st.session_state:
            st.session_state.google_api_key = google_api_key
            st.session_state.setup_complete = True
            st.success("✅ Setup complete!")
            st.experimental_rerun()
    
    return google_api_key