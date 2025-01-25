import streamlit as st
import json
import time
from datetime import datetime
from typing import Tuple, Dict

# Constants
BACKUP_VERSION = "1.0"
MAX_BACKUP_SIZE_MB = 10

def cleanup_import_state():
    """Clean up import-related session state variables"""
    if 'state_import' in st.session_state:
        del st.session_state.state_import

def check_response(response) -> bool:
    """Validate response from the model"""
    if not response:
        return False
    if isinstance(response, (list, dict)) and len(response) == 0:
        return False
    return True

def validate_export_state() -> bool:
    """Validate that there's data to export"""
    try:
        if not hasattr(st.session_state, 'model'):
            return False
        if not hasattr(st.session_state.model, 'database'):
            return False
            
        # Check if database has data by checking if it's empty
        database_dict = st.session_state.model.database.to_dict()
        if not database_dict:
            return False
            
        # Additional validation to ensure data structure
        if isinstance(database_dict, (list, dict)):
            return bool(len(database_dict) > 0)
        return False
    except Exception as e:
        st.error(f"Error validating export state: {str(e)}")
        return False

def validate_imported_data(data: dict) -> bool:
    """Validate the structure of imported data"""
    try:
        required_keys = {"metrics", "vector_database", "chat_history"}
        
        # Check if all required keys exist
        if not all(key in data for key in required_keys):
            return False
        
        # Validate metrics structure
        if not isinstance(data["metrics"], dict):
            return False
            
        # Validate chat history structure
        if not isinstance(data["chat_history"], list):
            return False
            
        # Validate vector database structure
        if not isinstance(data["vector_database"], dict):
            return False
            
        # Check if vector database has content
        if not data["vector_database"]:
            st.warning("⚠️ Imported state has no website data. You may need to process a website.")
            
        return True
    except Exception:
        return False

def handle_import_error(error: Exception) -> str:
    """Return user-friendly error messages"""
    if isinstance(error, json.JSONDecodeError):
        return "Invalid JSON format in backup file"
    elif isinstance(error, KeyError):
        return "Missing required data in backup file"
    elif isinstance(error, ValueError):
        return "Invalid data format in backup file"
    elif isinstance(error, IndexError):
        return "Empty or invalid data structure in backup file"
    return f"Import failed: {str(error)}"

def check_file_size(file_content: str) -> bool:
    """Check if file size is within limits"""
    try:
        size_mb = len(file_content.encode('utf-8')) / (1024 * 1024)
        return size_mb <= MAX_BACKUP_SIZE_MB
    except Exception:
        return False

def show_progress_bar(message: str):
    """Show a progress bar with a message"""
    try:
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.01)
        progress_bar.empty()
    except Exception:
        pass  # Silently fail if progress bar fails

def check_model_state() -> bool:
    """Check if the model has data loaded either from URL or import"""
    try:
        database_dict = st.session_state.model.database.to_dict()
        has_data = bool(database_dict and len(database_dict) > 0)
        if has_data:
            st.session_state.url_processed = True
        return st.session_state.url_processed
    except Exception:
        return False