import streamlit as st
import asyncio
from core.LLMBasedCrawler import Model
import os
import json
import time
from datetime import datetime
from core.LLMBasedCrawler import Model
from utils.monitoring import MetricsCollector, Metrics
from utils.progress import ProgressTracker
from utils.data_manager import DataManager
from utils.content_validator import ContentValidator

# Constants
BACKUP_VERSION = "1.0"
MAX_BACKUP_SIZE_MB = 10

# Helper functions for import/export
def cleanup_import_state():
    """Clean up import-related session state variables"""
    if 'state_import' in st.session_state:
        del st.session_state.state_import

def check_response(response):
    """Validate response from the model"""
    if not response:
        return False
    if isinstance(response, (list, dict)) and len(response) == 0:
        return False
    return True

def validate_export_state():
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

def check_model_state():
    """Check if the model has data loaded either from URL or import"""
    try:
        database_dict = st.session_state.model.database.to_dict()
        has_data = bool(database_dict and len(database_dict) > 0)
        if has_data:
            st.session_state.url_processed = True
        return st.session_state.url_processed
    except Exception:
        return False

# Configure Streamlit page
st.set_page_config(
    page_title="CrawlGPT Chat",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "model" not in st.session_state:
    st.session_state.model = Model()
    st.session_state.url_processed = False
    st.session_state.messages = []
    st.session_state.last_auto_backup = None

cleanup_import_state()

# Helper function to process URL
async def process_url(url):
    try:
        success, message = await st.session_state.model.extract_content_from_url(url)
        if success:
            # Verify that we actually got data
            database_data = st.session_state.model.database.to_dict()
            if database_data and len(database_data) > 0:
                st.session_state.url_processed = True
                return True, "Website processed successfully!"
            else:
                return False, "No content was extracted from the URL"
        return False, message
    except IndexError:
        return False, "Error: No content found at the specified URL"
    except Exception as e:
        return False, f"Error processing URL: {str(e)}"

# Main UI
st.title("CrawlGPT Chat Interface 🤖")

# URL Input and Processing
with st.sidebar:
    st.header("📝 Website Input")
    url = st.text_input("Enter website URL to analyze:")
    
    if st.button("Process Website"):
        if url:
            with st.spinner("Processing website content..."):
                success, message = asyncio.run(process_url(url))
                if success:
                    st.session_state.url_processed = True
                    st.success("✅ Website processed successfully!")
                else:
                    st.error(f"❌ Error: {message}")
                    st.session_state.url_processed = False
        else:
            st.warning("⚠️ Please enter a URL first.")

    # Model Configuration
    st.header("⚙️ Chat Settings")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    max_tokens = st.slider("Max Tokens", min_value=100, max_value=2000, value=500, step=100)
    model_name = st.selectbox(
        "Model",
        options=["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma-7b-it"],
        index=0
    )
    use_summary = st.checkbox("Use Summaries", value=False)
    
    # Check model state and display metrics
    check_model_state()
    
    # Display Metrics
    if st.session_state.url_processed:
        st.header("📊 Metrics")
        try:
            metrics = st.session_state.model.metrics_collector.metrics.to_dict()
            if metrics:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Requests", metrics.get("total_requests", 0))
                    st.metric("Successful", metrics.get("successful_requests", 0))
                with col2:
                    st.metric("Avg Response", f"{metrics.get('average_response_time', 0):.2f}s")
                    if "total_tokens_used" in metrics:
                        st.metric("Total Tokens", metrics["total_tokens_used"])
        except Exception as e:
            st.error(f"Error displaying metrics: {str(e)}")

    # Enhanced Data Management Section
    st.header("💾 Data Management")
    
    # Export functionality with progress and validation
    if st.button("Export Current State"):
        if not validate_export_state():
            st.warning("⚠️ No data to export. Please process a website first.")
        else:
            try:
                with st.spinner("Preparing export..."):
                    show_progress_bar("Exporting data")
                    export_data = {
                        "version": BACKUP_VERSION,
                        "timestamp": datetime.now().isoformat(),
                        "metrics": st.session_state.model.metrics_collector.metrics.to_dict(),
                        "vector_database": st.session_state.model.database.to_dict(),
                        "chat_history": st.session_state.messages
                    }
                    
                    # Convert to JSON string
                    export_json = json.dumps(export_data)
                    
                    if check_file_size(export_json):
                        # Show download button immediately after successful export
                        st.success("✅ Data exported successfully!")
                        st.download_button(
                            label="📥 Download Backup",
                            data=export_json,
                            file_name=f"crawlgpt_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            key="download_button"
                        )
                    else:
                        st.error(f"❌ Export failed: Backup size exceeds {MAX_BACKUP_SIZE_MB}MB limit")
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")

    # Import functionality with validation and progress
    uploaded_file = st.file_uploader("Import Previous State", type=['json'], key="state_import")
    if uploaded_file is not None:
        if st.button("Confirm Import"):
            try:
                with st.spinner("Importing data..."):
                    show_progress_bar("Importing backup")
                    file_content = uploaded_file.read()
                    if not file_content:
                        st.error("❌ Empty file uploaded")
                        cleanup_import_state()
                        
                    imported_data = json.loads(file_content)
                    if validate_imported_data(imported_data):
                        # Import the state
                        st.session_state.model.import_state(imported_data)
                        
                        # Set messages
                        if "chat_history" in imported_data:
                            st.session_state.messages = imported_data["chat_history"]
                        
                        # Set url_processed to True if we have data in the vector database
                        if imported_data.get("vector_database"):
                            st.session_state.url_processed = True
                        
                        # Clear the file uploader from session state
                        st.session_state.state_import = None
                        st.success("✅ Data imported successfully!")
                        
                        # Display imported state info
                        st.info("📊 Imported State Info:")
                        if "timestamp" in imported_data:
                            st.write(f"Backup Date: {imported_data['timestamp']}")
                        if "version" in imported_data:
                            st.write(f"Backup Version: {imported_data['version']}")
                        st.write(f"Chat History: {len(imported_data['chat_history'])} messages")
                        st.write(f"Vector Database Size: {len(imported_data.get('vector_database', {}))} entries")
                        
                        st.balloons()
                        time.sleep(2)  # Give time for the user to see the info
                        st.experimental_rerun()
                    else:
                        st.error("❌ Invalid backup file format")
            except Exception as e:
                st.error(handle_import_error(e))

    # Backup Management Section
    if st.session_state.url_processed:
        with st.expander("🔄 Backup Management"):
            st.write("Previous Backups")
            
            # Add auto-backup option
            enable_auto_backup = st.checkbox("Enable Auto-backup", value=False)
            if enable_auto_backup:
                auto_backup_interval = st.slider(
                    "Auto-backup interval (minutes)",
                    min_value=5,
                    max_value=60,
                    value=15
                )

# Chat Interface
st.markdown("### 💬 Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about the website content..."):
    database_has_data = bool(st.session_state.model.database.to_dict())
    if not st.session_state.url_processed and not database_has_data:
        st.warning("⚠️ Please process a website first!")
    else:
        try:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.model.generate_response(
                            query=prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            model=model_name,
                            use_summary=use_summary
                        )
                        if check_response(response):
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            st.error("No valid response generated. The model might not have enough context.")
                    except IndexError:
                        st.error("Error: Unable to generate response. Please try processing the website again.")
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
        except Exception as e:
            st.error(f"Error in chat processing: {str(e)}")

# Clear chat button
if st.session_state.messages:
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Debug section
if st.sidebar.checkbox("🔍 Show Debug Info"):
    try:
        st.sidebar.json(metrics)
    except Exception:
        st.sidebar.warning("No metrics available")

# Auto-backup logic
if (
    "enable_auto_backup" in locals() 
    and enable_auto_backup 
    and st.session_state.last_auto_backup is not None
):
    current_time = datetime.now()
    time_diff = (current_time - st.session_state.last_auto_backup).total_seconds() / 60
    
    if time_diff >= auto_backup_interval:
        try:
            export_data = {
                "version": BACKUP_VERSION,
                "timestamp": current_time.isoformat(),
                "metrics": st.session_state.model.metrics_collector.metrics.to_dict(),
                "vector_database": st.session_state.model.database.to_dict(),
                "chat_history": st.session_state.messages
            }
            export_json = json.dumps(export_data)
            st.session_state.last_auto_backup = current_time
            
            # Save auto-backup
            backup_filename = f"auto_backup_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
            st.info(f"Auto-backup created: {backup_filename}")
        except Exception as e:
            st.error(f"Auto-backup failed: {str(e)}")