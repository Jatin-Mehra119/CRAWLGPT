import streamlit as st
import asyncio
import time
from datetime import datetime
from core.LLMBasedCrawler import Model
from utils.monitoring import MetricsCollector
from utils.progress import ProgressTracker
from utils.data_manager import DataManager
from utils.content_validator import ContentValidator

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

if "use_summary" not in st.session_state:
    st.session_state.use_summary = True

if "metrics" not in st.session_state:
    st.session_state.metrics = MetricsCollector()

model = st.session_state.model

# Sidebar for metrics and monitoring
with st.sidebar:
    st.subheader("📊 System Metrics")
    metrics = st.session_state.metrics.metrics.to_dict()
    st.metric("Total Requests", metrics["total_requests"])
    st.metric("Success Rate", f"{(metrics['successful_requests']/max(metrics['total_requests'], 1))*100:.1f}%")
    st.metric("Avg Response Time", f"{metrics['average_response_time']:.2f}s")
    
    # Export/Import Data
    st.subheader("💾 Data Management")
    if st.button("Export Current State"):
        try:
            export_path = st.session_state.data_manager.export_data({
                "metrics": metrics,
                "vector_database": model.database.to_dict()
            }, f"crawlgpt_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            st.success(f"Data exported to: {export_path}")
        except Exception as e:
            st.error(f"Export failed: {e}")

    uploaded_file = st.file_uploader("Import Previous State", type=['json', 'pkl'])
    if uploaded_file is not None:
        try:
            imported_data = st.session_state.data_manager.import_data(uploaded_file)
            model.import_state(imported_data)
            st.success("Data imported successfully!")
        except Exception as e:
            st.error(f"Import failed: {e}")

# URL input and content extraction
url = st.text_input("Enter URL:", help="Provide the URL to extract content from.")

if st.button("Extract and Store Content"):
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Validate URL
            if not st.session_state.content_validator.is_valid_url(url):
                st.error("Invalid URL format")
            else:
                async def extract_content():
                    start_time = time.time()
                    
                    # Initialize progress tracker
                    progress = ProgressTracker(
                        total_steps=4,
                        operation_name="content_extraction"
                    )
                    
                    try:
                        # Update progress for each step
                        status_text.text("Validating URL...")
                        progress_bar.progress(25)
                        
                        status_text.text("Crawling content...")
                        progress_bar.progress(50)
                        await model.extract_content_from_url(url)
                        
                        status_text.text("Processing content...")
                        progress_bar.progress(75)
                        
                        status_text.text("Storing in database...")
                        progress_bar.progress(100)
                        
                        # Record metrics
                        st.session_state.metrics.record_request(
                            success=True,
                            response_time=time.time() - start_time,
                            tokens_used=len(model.context.split())
                        )
                        
                        st.success("Content extracted and stored successfully.")
                        st.write("Extracted Content Preview:")
                        st.write(model.context[:500])
                        
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

                # Run the asynchronous function
                asyncio.run(extract_content())
                
        except Exception as e:
            st.error(f"Error extracting content: {e}")

# Query section with RAG type selection
rag_type = st.radio(
    "Select RAG Type:",
    ("Normal RAG", "Summarized RAG")
)

query = st.text_input("Ask a question:", help="Enter a query to retrieve context and generate a response.")
temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.slider("Max Tokens", 50, 1000, 200)
model_id = st.text_input("Model ID", "llama-3.1-8b-instant")

if st.button("Get Response"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        try:
            start_time = time.time()
            
            if rag_type == "Normal RAG":
                response = model.generate_response(
                    query, 
                    temperature, 
                    max_tokens, 
                    model_id, 
                    use_summary=False
                )
            else:
                response = model.generate_response(
                    query, 
                    temperature, 
                    max_tokens, 
                    model_id, 
                    use_summary=True
                )
            
            # Record metrics
            st.session_state.metrics.record_request(
                success=True,
                response_time=time.time() - start_time,
                tokens_used=len(response.split())
            )
            
            st.write("Generated Response:")
            st.write(response)
            
        except Exception as e:
            st.session_state.metrics.record_request(
                success=False,
                response_time=time.time() - start_time,
                tokens_used=0
            )
            st.error(f"Error generating response: {e}")

# Enhanced debug section
if st.checkbox("Show Debug Info"):
    st.subheader("🔍 Debug Information")
    
    # System Status
    st.write("System Status:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Cache Information:")
        st.write(model.cache)
    
    with col2:
        st.write("Current Metrics:")
        st.write(metrics)
    
    # Content Preview
    st.write("Current Context Preview:")
    st.write(model.context[:500])

# Clear functionality with confirmation
if st.button("Clear All Data"):
    if st.checkbox("Confirm Clear"):
        try:
            model.clear()
            st.session_state.metrics = MetricsCollector()  # Reset metrics
            st.success("All data cleared successfully.")
        except Exception as e:
            st.error(f"Error clearing data: {e}")