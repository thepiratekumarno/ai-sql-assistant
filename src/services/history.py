import streamlit as st
import uuid
from datetime import datetime

def init_history():
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

def save_query_to_history(query, result):
    try:
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "query": query,
            "result": str(type(result))
        }
        st.session_state.query_history.insert(0, entry)
    except:
        pass

def show_query_history():
    if not st.session_state.query_history:
        st.sidebar.info("No history yet")
        return
        
    st.sidebar.subheader("📜 Query History")
    for entry in st.session_state.query_history[:5]:
        st.sidebar.caption(f"{entry['timestamp']}: {entry['query']}")