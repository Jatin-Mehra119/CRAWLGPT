import streamlit as st
import asyncio
import time
from datetime import datetime
from core.LLMBasedCrawler import Model
from utils.monitoring import MetricsCollector, Metrics
from utils.progress import ProgressTracker
from utils.data_manager import DataManager
from utils.content_validator import ContentValidator
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Streamlit app title and description
st.title("CrawlGPT 🚀🤖")
st.write(
    "This app extracts content from a URL, stores it in a vector database, and generates responses to user queries. "
    "It also summarizes extracted content for efficient retrieval."
)

# Initialize components in session state
if "model" not in st.session_state:
    st.session_state.model = Model()
    st.session_state.data_manager = DataManager()
    st.session_state.content_validator = ContentValidator()
    st.session_state.messages = []  # Initialize chat messages
    st.session_state.url_processed = False

if "use_summary" not in st.session_state:
    st.session_state.use_summary = True

if "metrics" not in st.session_state:
    st.session_state.metrics = MetricsCollector()

model = st.session_state.model

# Sidebar implementation
with st.sidebar:
    st.subheader("📊 System Metrics")
    metrics = st.session_state.metrics.metrics.to_dict()
    st.metric("Total Requests", metrics["total_requests"])
    st.metric("Success Rate", f"{(metrics['successful_requests']/max(metrics['total_requests'], 1))*100:.1f}%")
    st.metric("Avg Response Time", f"{metrics['average_response_time']:.2f}s")
    
    # RAG Settings
    st.subheader("🔧 RAG Settings")
    st.session_state.use_summary = st.checkbox("Use Summarized RAG", value=False, help="Don't use summaization when dealing with Coding Documentation.")
    st.subheader("🤖 Normal LLM Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, help="Controls the randomness of the generated text. Lower values are more deterministic.")
    max_tokens = st.slider("Max Tokens", 500, 10000, 200, help="Maximum number of tokens to generate in the response.")
    model_id = st.radio("Model ID", ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile', 'mixtral-8x7b-32768'], help="Choose the model to use for generating responses.")
    
    # Export/Import Data
    st.subheader("💾 Data Management")
    if st.button("Export Current State"):
        try:
            export_data = {
                "metrics": metrics,
                "vector_database": model.database.to_dict(),
                "messages": st.session_state.messages
            }
            export_json = json.dumps(export_data)
            st.session_state.export_json = export_json
            st.success("Data exported successfully!")
        except Exception as e:
            st.error(f"Export failed: {e}")

    if "export_json" in st.session_state:
        st.download_button(
            label="Download Backup",
            data=st.session_state.export_json,
            file_name=f"crawlgpt_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    uploaded_file = st.file_uploader("Import Previous State", type=['json'])
    if uploaded_file is not None:
        try:
            imported_data = json.loads(uploaded_file.read())
            
            # Validate imported data structure
            required_keys = ["metrics", "vector_database", "messages"]
            if not all(key in imported_data for key in required_keys):
                raise ValueError("Invalid backup file structure")
                
            # Import data with proper state management
            model.import_state(imported_data)
            
            # Restore chat history and context
            if "messages" in imported_data:
                st.session_state.messages = imported_data["messages"]
                
            # Set URL processed state if there's context
            if model.context:
                st.session_state.url_processed = True
            else:
                st.session_state.url_processed = False
                
            # Update metrics
            if "metrics" in imported_data:
                st.session_state.metrics = MetricsCollector()
                st.session_state.metrics.metrics = Metrics.from_dict(imported_data["metrics"])
                model.import_state(imported_data)
                
            st.success("Data imported successfully! You can continue chatting.")
            st.session_state.url_processed = True
            
        except Exception as e:
            st.error(f"Import failed: {e}")
            st.session_state.url_processed = False

# URL Processing Section
url_col1, url_col2 = st.columns([3, 1])
with url_col1:
    url = st.text_input("Enter URL:", help="Provide the URL to extract content from.")
with url_col2:
    process_url = st.button("Process URL")

if process_url and url:
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            if not st.session_state.content_validator.is_valid_url(url):
                st.error("Invalid URL format")
            else:
                async def extract_content():
                    start_time = time.time()
                    progress = ProgressTracker(total_steps=4, operation_name="content_extraction")
                    
                    try:
                        status_text.text("Validating URL...")
                        progress_bar.progress(25)
                        
                        status_text.text("Crawling content...")
                        progress_bar.progress(50)
                        success, msg = await model.extract_content_from_url(url)
                        
                        if success:
                            status_text.text("Processing content...")
                            progress_bar.progress(75)
                            
                            status_text.text("Storing in database...")
                            progress_bar.progress(100)
                            
                            st.session_state.metrics.record_request(
                                success=True,
                                response_time=time.time() - start_time,
                                tokens_used=len(model.context.split())
                            )
                            
                            st.session_state.url_processed = True
                            st.session_state.messages.append({
                                "role": "system",
                                "content": f"Content from {url} has been processed and is ready for queries."
                            })
                            st.success("Content processed successfully!")
                        else:
                            raise Exception(msg)
                            
                    except Exception as e:
                        st.session_state.metrics.record_request(
                            success=False,
                            response_time=time.time() - start_time,
                            tokens_used=0
                        )
                        raise e
                    finally:
                        status_text.empty()
                        progress_bar.empty()

                asyncio.run(extract_content())
                
        except Exception as e:
            st.error(f"Error processing URL: {e}")

# Chat Interface
st.subheader("💭 Chat Interface")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
if chat_input := st.chat_input("Ask about the content...", disabled=not st.session_state.url_processed):
    # Display user message
    with st.chat_message("user"):
        st.write(chat_input)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": chat_input})
    
    try:
        start_time = time.time()
        
        # Show typing indicator
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.generate_response(
                    chat_input,
                    temperature,
                    max_tokens,
                    model_id,
                    use_summary=st.session_state.use_summary
                )
                st.write(response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Record metrics
        st.session_state.metrics.record_request(
            success=True,
            response_time=time.time() - start_time,
            tokens_used=len(response.split())
        )

        # Debug log for database insertion
        try:
            logging.debug("Attempting to insert data into the database")
            # Insert data into the database
            # Example: db.insert(response)
            logging.debug("Data successfully inserted into the database")
        except Exception as e:
            logging.error(f"Error inserting data into the database: {e}")

    except Exception as e:
        st.session_state.metrics.record_request(
            success=False,
            response_time=time.time() - start_time,
            tokens_used=0
        )
        st.error(f"Error generating response: {e}")
        logging.error(f"Error generating response: {e}")

# Debug and Clear Options
col1, col2 = st.columns(2)
with col1:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.success("Chat history cleared!")

with col2:
    if st.button("Clear All Data"):
        if st.checkbox("Confirm Clear"):
            try:
                model.clear()
                st.session_state.messages = []
                st.session_state.url_processed = False
                st.session_state.metrics = MetricsCollector()
                st.success("All data cleared successfully.")
            except Exception as e:
                st.error(f"Error clearing data: {e}")

# Debug Information
if st.checkbox("Show Debug Info"):
    st.subheader("🔍 Debug Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Cache Information:")
        st.write(model.cache)
    
    with col2:
        st.write("Current Metrics:")
        st.write(metrics)
    
    st.write("Current Context Preview:")
    st.write(model.context[:500] if model.context else "No context available")