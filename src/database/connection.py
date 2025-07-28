import mysql.connector
from mysql.connector import Error
import streamlit as st

def get_db_connection(credentials, database=None):
    """Get direct database connection"""
    try:
        conn = mysql.connector.connect(
            host=credentials["host"],
            user=credentials["user"],
            password=credentials["password"],
            port=credentials["port"],
            database=database
        )
        return conn
    except Error as e:
        st.error(f"❌ Connection failed: {str(e)}")
        return None

def test_connection(credentials):
    """Test database connection"""
    try:
        conn = get_db_connection(credentials)
        if conn and conn.is_connected():
            conn.close()
            return True
        return False
    except Error:
        return False