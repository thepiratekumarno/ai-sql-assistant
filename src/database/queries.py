from .connection import get_db_connection
from mysql.connector import Error
import streamlit as st

def execute_query(credentials, database, query, params=None, fetch=True):
    """Execute SQL query with proper transaction handling"""
    conn = get_db_connection(credentials, database)
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        # Determine if it's a read or write operation
        is_write_operation = query.strip().lower().startswith(
            ('insert', 'update', 'delete', 'create', 'alter', 'drop', 'replace')
        )
        
        if fetch and not is_write_operation:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
            conn.commit()  # Commit for write operations
            
        return result
    except Error as e:
        st.error(f"❌ SQL Error: {str(e)}")
        conn.rollback()  # Rollback on error
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()