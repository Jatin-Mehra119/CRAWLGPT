import streamlit as st
import asyncio
from core.LLMBasedCrawler import Model
import os
from dotenv import load_dotenv
from datetime import datetime
from core.LLMBasedCrawler import Model
from utils.monitoring import MetricsCollector, Metrics
from utils.progress import ProgressTracker
from utils.data_manager import DataManager
from utils.content_validator import ContentValidator

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="CrawlGPT Chat",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "model" not in st.session_state:
    st.session_state.model = Model()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "url_processed" not in st.session_state:
    st.session_state.url_processed = False

# Helper function to process URL
async def process_url(url):
    success, message = await st.session_state.model.extract_content_from_url(url)
    return success, message

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
        else:
            st.warning("⚠️ Please enter a URL first.")

    # Model Configuration
    st.header("⚙️ Chat Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Max Tokens", 100, 2000, 500)
    model_name = st.selectbox(
        "Model",
        ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma-7b-it"]
    )
    use_summary = st.checkbox("Use Summaries", value=True)
    
    # Display Metrics
    if st.session_state.url_processed:
        st.header("📊 Metrics")
        metrics = st.session_state.model.metrics_collector.metrics.to_dict()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Requests", metrics["total_requests"])
            st.metric("Successful", metrics["successful_requests"])
        with col2:
            st.metric("Avg Response", f"{metrics['average_response_time']:.2f}s")
            if "total_tokens_used" in metrics:
                st.metric("Total Tokens", metrics["total_tokens_used"])

# Chat Interface
st.markdown("### 💬 Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about the website content..."):
    if not st.session_state.url_processed:
        st.warning("⚠️ Please process a website first!")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.model.generate_response(
                    query=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model_name,
                    use_summary=use_summary
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Clear chat button
if st.session_state.messages:
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Debug section
if st.sidebar.checkbox("🔍 Show Debug Info"):
    st.sidebar.json(metrics)