# CRAWLGPT 🤖

A powerful web content crawler with LLM-powered summarization and chat capabilities. CRAWLGPT extracts content from URLs, stores it in a vector database (FAISS), and enables natural language querying of the stored content. It combines modern web crawling technology with advanced language models to help you extract, analyze, and interact with web content intelligently.

## 🌟 Features

-   **Web Crawling**  
    Async-based crawling powered by [crawl4ai](https://pypi.org/project/crawl4ai/) and Playwright.  
    Includes configurable rate limiting and content validation.
    
-   **Content Processing**  
    Automatically chunks large texts, generates embeddings, and summarizes text via the Groq API.
    
-   **Chat Interface**  
    Streamlit-based UI with a user-friendly chat panel.  
    Supports summarized or full-text retrieval (RAG) for context injection.
    
-   **Data Management**  
    Stores content in a local or in-memory vector database (FAISS) for efficient retrieval.  
    Tracks usage metrics and supports import/export of system state.
    
-   **Testing**  
    Comprehensive unit and integration tests using Python’s `unittest` framework.
    

## 🎥 Demo
### [Deployed APP 🚀🤖](https://huggingface.co/spaces/jatinmehra/CRAWL-GPT-CHAT)

[streamlit-chat_app video.webm](https://github.com/user-attachments/assets/ae1ddca0-9e3e-4b00-bf21-e73bb8e6cfdf)
  
_Example of CRAWLGPT in action!_

## 🔧 Requirements

-   Python >= 3.8
-   Operating System: OS Independent
-   Required packages are handled by the setup script.


## 🚀 Quick Start

1.  Clone the Repository:
    
    ```git clone https://github.com/Jatin-Mehra119/CRAWLGPT.git
    cd CRAWLGPT
    ```
    
2.  Run the Setup Script:

    ```
    python -m setup_env
    ``` 
    
    _This script installs dependencies, creates a virtual environment, and prepares the project._
    
3.  Update Your Environment Variables:
    
    -   Create or modify the `.env` file.
    -   Add your Groq API key and Ollama API key. Learn how to get API keys.
    
    
    ```
    GROQ_API_KEY=your_groq_api_key_here
    OLLAMA_API_TOKEN=your_ollama_api_key_here
    ```
    
4.  Activate the Virtual Environment:
    
    ```
    source .venv/bin/activate  # On Unix/macOS
    .venv\Scripts\activate  # On Windows
    ``` 
    
5.  Run the Application:
	```
	python -m streamlit run src/crawlgpt/ui/chat_app.py
	```

## 📦 Dependencies

### Core Dependencies

-   `streamlit==1.41.1`
-   `groq==0.15.0`
-   `sentence-transformers==3.3.1`
-   `faiss-cpu==1.9.0.post1`
-   `crawl4ai==0.4.247`
-   `python-dotenv==1.0.1`
-   `pydantic==2.10.5`
-   `aiohttp==3.11.11`
-   `beautifulsoup4==4.12.3`
-   `numpy==2.2.0`
-   `tqdm==4.67.1`
-   `playwright>=1.41.0`
-   `asyncio>=3.4.3`

### Development Dependencies

-   `pytest==8.3.4`
-   `pytest-mockito==0.0.4`
-   `black==24.2.0`
-   `isort==5.13.0`
-   `flake8==7.0.0`

## 🏗️ Project Structure


```
crawlgpt/
├── src/
│   └── crawlgpt/
│       ├── core/
│       │   ├── DatabaseHandler.py
│       │   ├── LLMBasedCrawler.py 
│       │   └── SummaryGenerator.py
│       ├── ui/
│       │   ├── chat_app.py
│       │   └── chat_ui.py
│       └── utils/
│           ├── content_validator.py
│           ├── data_manager.py
│           ├── helper_functions.py
│           ├── monitoring.py
│           └── progress.py
├── tests/
│   └── test_core/
│       ├── test_database_handler.py
│       ├── test_integration.py
│       ├── test_llm_based_crawler.py
│       └── test_summary_generator.py
├── .github/
│   └── workflows/
│       └── Push_to_hf.yaml
├── .gitignore
├── LICENSE
├── README.md
├── Docs
├── pyproject.toml
├── pytest.ini
└── setup_env.py
``` 

## 🧪 Testing

Run all tests
```
python -m pytest
```
_The tests include unit tests for core functionality and integration tests for end-to-end workflows._

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

-   [Bug Tracker](https://github.com/Jatin-Mehra119/crawlgpt/issues)
-   [Documentation](https://github.com/Jatin-Mehra119/crawlgpt/wiki)
-   [Source Code](https://github.com/Jatin-Mehra119/crawlgpt)

## 🧡 Acknowledgments

-   Inspired by the potential of GPT models for intelligent content processing.
-   Special thanks to the creators of Crawl4ai, Groq, FAISS, and Playwright for their powerful tools.

## 👨‍💻 Author

-   Jatin Mehra (jatinmehra@outlook.in)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, open an issue first to discuss your proposal.

1.  Fork the Project.
2.  Create your Feature Branch:
    ```
    git checkout -b feature/AmazingFeature`
    ```
3.  Commit your Changes:
    ```
    git commit -m 'Add some AmazingFeature
    ```
4.  Push to the Branch:
    ```
    git push origin feature/AmazingFeature
    ```
5.  Open a Pull Request.
