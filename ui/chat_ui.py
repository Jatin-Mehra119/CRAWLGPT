import streamlit as st
import asyncio
from core.LLMBasedCrawler import Model

# Streamlit app title and description
st.title("CrawlGPT 🚀🤖")
st.write(
    "This app extracts content from a URL, stores it in a vector database, and generates responses to user queries. "
    "It also summarizes extracted content for efficient retrieval."
)

# Initialize the Model object in session state
if "model" not in st.session_state:
    st.session_state.model = Model()

if "use_summary" not in st.session_state:
    st.session_state.use_summary = True  # Default to summarization-based RAG

model = st.session_state.model  # Access the persistent Model object

# URL input and content extraction
url = st.text_input("Enter URL:", help="Provide the URL to extract content from.")

if st.button("Extract and Store Content"):
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        try:
            async def extract_content():
                await model.extract_content_from_url(url)
                st.success("Content extracted and stored successfully.")
                st.write("Extracted Content Preview:")
                st.write(model.context[:500])  # Display the first 500 characters for debugging

            # Run the asynchronous function
            asyncio.run(extract_content())
        except Exception as e:
            st.error(f"Error extracting content: {e}")

# Toggle for summarization vs. normal RAG
st.session_state.use_summary = st.radio(
    "Select Retrieval Mode:",
    ("Summarization-based RAG", "Normal RAG"),
    index=0 if st.session_state.use_summary else 1
) == "Summarization-based RAG"

# Query input and response generation
query = st.text_input("Ask a question:", help="Enter a query to retrieve context and generate a response.")
temperature = st.slider("Temperature", 0.0, 1.0, 0.7, help="Adjust the randomness of the LLM's responses.")
max_tokens = st.slider("Max Tokens", 50, 1000, 200, help="Set the maximum number of tokens for the response.")
model_id = st.text_input("Model ID", "llama-3.1-8b-instant", help="Specify the LLM model ID to use.")

if st.button("Get Response"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        try:
            response = model.generate_response(
                query, 
                temperature, 
                max_tokens, 
                model_id, 
                use_summary=st.session_state.use_summary
            )
            st.write("Generated Response:")
            st.write(response)
        except Exception as e:
            st.error(f"Error generating response: {e}")

# Clear context and database
if st.button("Clear Context and Cache"):
    try:
        model.clear()
        st.success("Context and cache cleared successfully.")
    except Exception as e:
        st.error(f"Error clearing context and cache: {e}")

# Additional debugging and information
if st.checkbox("Show Debug Info"):
    st.write("Current Context:")
    st.write(model.context[:500])  # Display the first 500 characters of the context
    st.write("Cache Information:")
    st.write(model.cache)