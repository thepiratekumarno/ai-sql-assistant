import os
from dotenv import load_dotenv

def initialize_app():
    """Initialize application environment"""
    # Load environment variables
    load_dotenv()
    
    # Ensure required directories exist
    os.makedirs(".streamlit", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    
    # Initialize MongoDB (if needed)
    # This can be expanded to create collections/indexes
