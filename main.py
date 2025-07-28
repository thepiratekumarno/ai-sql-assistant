import streamlit as st
import extra_streamlit_components as stx
from src.services.auth import is_authenticated, logout, show_login_ui
from src.services.oauth import handle_oauth_callback
from src.services.setup import show_setup_ui
from src.services.history import init_history, save_query_to_history, show_query_history
from src.ai.query_generator import generate_sql_query
from src.ai.explainer import explain_query
from src.database.queries import execute_query
from src.database.schema import get_databases, get_tables, get_table_columns, create_table
from src.database.mongodb import get_user_credentials
from src.utils.visualization import visualize_data
from src.utils.helpers import prepare_data_for_export, get_column_types
import pandas as pd

# Initialize page config
st.set_page_config(
    page_title="AI SQL Assistant", 
    layout="wide", 
    page_icon="🤖"
)

# Initialize session state
def init_session_state():
    keys = [
        'setup_complete', 'current_query', 'explain_mode', 
        'visualization_type', 'selected_db', 'selected_table',
        'last_sql_query', 'last_explanation', 'last_execution_result',
        'user_info', 'mysql_creds', 'google_api_key', 'tables'
    ]
    default_values = {
        'setup_complete': False,
        'current_query': "",
        'explain_mode': True,
        'visualization_type': "Table",
        'selected_db': None,
        'selected_table': None,
        'last_sql_query': "",
        'last_explanation': "",
        'last_execution_result': None,
        'user_info': None,
        'mysql_creds': None,
        'google_api_key': None,
        'tables': []
    }
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = default_values.get(key, None)

init_session_state()

# Initialize history
init_history()

# Visualization options
VISUALIZATION_TYPES = ["Table", "Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot", "Histogram"]

# Check if we're handling an OAuth callback
if "oauth_provider" in st.session_state:
    handle_oauth_callback()

# Authentication check
if not is_authenticated():
    show_login_ui()
    st.stop()

# If authenticated, check if we have saved credentials
if not st.session_state.setup_complete:
    user_id = st.session_state.user_info["email"]
    saved_creds = get_user_credentials(user_id)
    
    if saved_creds:
        # Load saved credentials
        st.session_state.google_api_key = saved_creds.get("google_api_key")
        st.session_state.mysql_creds = saved_creds.get("mysql_creds")
        st.session_state.setup_complete = True
    else:
        show_setup_ui()
        st.stop()

# Main app function
def show_main_app():
    """Main application interface"""
    # Header
    st.title("🤖 AI-Powered SQL Assistant")
    st.caption(f"Welcome, {st.session_state.user_info['name']}! Interact with your MySQL database using natural language")
    
    # Sign out button
    if st.sidebar.button("Sign Out"):
        logout()
    
    # Database selection
    st.sidebar.subheader("🔧 Configuration")
    databases = get_databases(st.session_state.mysql_creds)
    if databases:
        selected_db = st.sidebar.selectbox("📁 Select Database", databases, key="db_selector")
        if selected_db != st.session_state.selected_db:
            st.session_state.selected_db = selected_db
            st.session_state.tables = get_tables(st.session_state.mysql_creds, selected_db)
    else:
        st.sidebar.info("No databases found")
    
    # Table selection
    if 'tables' in st.session_state and st.session_state.tables:
        selected_table = st.sidebar.selectbox("📊 Select Table", st.session_state.tables, key="table_selector")
        st.session_state.selected_table = selected_table
    
    # Schema display
    with st.sidebar.expander("📋 Table Schema", expanded=False):
        if st.session_state.selected_db and st.session_state.selected_table:
            columns = get_table_columns(
                st.session_state.mysql_creds,
                st.session_state.selected_db,
                st.session_state.selected_table
            )
            if columns:
                st.write(f"Table: `{st.session_state.selected_table}`")
                for column in columns:
                    st.code(column, language="plaintext")
            else:
                st.info("No columns found")
        else:
            st.info("Select a database and table")
    
    # Table creation UI
    with st.sidebar.expander("➕ Create Table", expanded=False):
        table_name = st.text_input("Table Name")
        num_columns = st.number_input("Number of Columns", 1, 10, 3)
        
        columns = []
        for i in range(num_columns):
            col1, col2 = st.columns(2)
            with col1:
                col_name = st.text_input(f"Column {i+1} Name", key=f"col_name_{i}")
            with col2:
                col_type = st.selectbox(f"Type", get_column_types(), key=f"col_type_{i}")
            columns.append({"name": col_name, "type": col_type})
        
        if st.button("Create Table") and table_name:
            if create_table(
                st.session_state.mysql_creds,
                st.session_state.selected_db,
                table_name,
                columns
            ):
                st.success(f"✅ Table '{table_name}' created!")
                st.session_state.tables = get_tables(st.session_state.mysql_creds, st.session_state.selected_db)
                st.session_state.selected_table = table_name
                st.rerun()
    
    # Settings
    st.session_state.explain_mode = st.sidebar.checkbox("Explain queries", value=True)
    
    # History
    show_query_history()
    
    # Command input area
    st.subheader("💬 Enter Your Command")
    user_input = st.text_area(
        "Database command:", 
        value=st.session_state.current_query,
        placeholder="e.g., 'Add new mouse: name Harsh, age 22' or 'Show all users'",
        height=100,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        execute_btn = st.button("🚀 Execute Command", type="primary")
    
    # Execution flow
    if execute_btn and user_input and st.session_state.selected_db and st.session_state.selected_table:
        st.session_state.current_query = user_input
        
        # Generate SQL
        with st.spinner("Generating SQL query..."):
            sql_query = generate_sql_query(
                st.session_state.google_api_key,
                user_input,
                st.session_state.mysql_creds,
                st.session_state.selected_db,
                st.session_state.selected_table
            )
        
        # Handle generation errors
        if isinstance(sql_query, dict) and "error" in sql_query:
            st.error(f"❌ Generation Error: {sql_query['error']}")
            return
        
        # Store generated SQL in session state
        st.session_state.last_sql_query = sql_query
        
        # Explain query
        if st.session_state.explain_mode:
            with st.spinner("Generating explanation..."):
                explanation = explain_query(st.session_state.google_api_key, sql_query)
            # Store explanation in session state
            st.session_state.last_explanation = explanation
        else:
            st.session_state.last_explanation = ""
        
        # Execute query
        with st.spinner("Executing query..."):
            # Determine if it's a read or write operation
            is_read_operation = sql_query.strip().lower().startswith(
                ('select', 'show', 'describe', 'explain')
            )
            
            execution_result = execute_query(
                st.session_state.mysql_creds,
                st.session_state.selected_db,
                sql_query,
                fetch=is_read_operation
            )
        
        # Store execution result in session state
        st.session_state.last_execution_result = execution_result
        
        # Save to history
        save_query_to_history(user_input, execution_result)
        
        # Refresh table data after write operations
        if not is_read_operation:
            st.session_state.tables = get_tables(st.session_state.mysql_creds, st.session_state.selected_db)
    
    # Display previous results if they exist
    if st.session_state.last_sql_query:
        # Display generated SQL
        with st.expander("Generated SQL", expanded=True):
            st.code(st.session_state.last_sql_query, language="sql")
        
        # Display explanation
        if st.session_state.last_explanation:
            st.info(f"💡 Explanation: {st.session_state.last_explanation}")
        
        # Display results
        if st.session_state.last_execution_result is None:
            st.error("Execution failed")
        elif isinstance(st.session_state.last_execution_result, list):
            st.subheader("📊 Results")
            if st.session_state.last_execution_result:
                # Export option
                df = prepare_data_for_export(st.session_state.last_execution_result)
                st.download_button(
                    "💾 Export CSV",
                    df.to_csv(index=False).encode('utf-8'),
                    f"{st.session_state.selected_table}.csv"
                )
                
                # Visualization
                st.session_state.visualization_type = st.selectbox(
                    "Visualization Type", 
                    VISUALIZATION_TYPES,
                    key="viz_select"
                )
                viz_result = visualize_data(st.session_state.last_execution_result, st.session_state.visualization_type)
                
                if isinstance(viz_result, pd.DataFrame):
                    st.dataframe(viz_result, use_container_width=True)
                else:
                    st.plotly_chart(viz_result, use_container_width=True)
            else:
                st.info("No results returned")
        elif isinstance(st.session_state.last_execution_result, int):
            st.success(f"✅ Rows affected: {st.session_state.last_execution_result}")

# Run the main app
show_main_app()
