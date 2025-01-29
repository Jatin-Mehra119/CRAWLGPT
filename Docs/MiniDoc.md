# CrawlGPT Documentation

## Overview

CrawlGPT is a web content crawler with GPT-powered summarization and chat capabilities. It extracts content from URLs, stores it in a vector database, and enables natural language querying of the stored content.

## Project Structure

```
crawlgpt/
├── src/
│   └── crawlgpt/
│       ├── core/                           # Core functionality
│       │   ├── database.py                 # SQL database handling
│       │   ├── LLMBasedCrawler.py         # Main crawler implementation
│       │   ├── DatabaseHandler.py          # Vector database (FAISS)
│       │   └── SummaryGenerator.py         # Text summarization
│       ├── ui/                            # User Interface
│       │   ├── chat_app.py                # Main Streamlit app
│       │   ├── chat_ui.py                 # Development UI
│       │   └── login.py                   # Authentication UI
│       └── utils/                         # Utilities
│           ├── content_validator.py        # URL/content validation
│           ├── data_manager.py            # Import/export handling
│           ├── helper_functions.py         # General helpers
│           ├── monitoring.py              # Metrics collection
│           └── progress.py                # Progress tracking
├── tests/                                # Test suite
│   └── test_core/
│       ├── test_database_handler.py       # Vector DB tests
│       ├── test_integration.py           # Integration tests
│       ├── test_llm_based_crawler.py     # Crawler tests
│       └── test_summary_generator.py     # Summarizer tests
├── .github/                             # CI/CD
│   └── workflows/
│       └── Push_to_hf.yaml              # HuggingFace sync
├── Docs/
│   └── MiniDoc.md                       # Documentation
├── .dockerignore                        # Docker exclusions
├── .gitignore                          # Git exclusions
├── Dockerfile                          # Container config
├── LICENSE                             # MIT License
├── README.md                          # Project documentation
├── README_hf.md                       # HuggingFace README
├── pyproject.toml                     # Project metadata
├── pytest.ini                         # Test configuration
└── setup_env.py                       # Environment setup
```

## Core Components

### [LLMBasedCrawler](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/core/LLMBasedCrawler.py) (src/crawlgpt/core/LLMBasedCrawler.py)

-   Main crawler class handling web content extraction and processing
-   Integrates with Groq API for language model operations
-   Manages content chunking, summarization and response generation
-   Includes rate limiting and metrics collection

### [DatabaseHandler](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/core/DatabaseHandler.py) (src/crawlgpt/core/DatabaseHandler.py)

-   Vector database implementation using FAISS
-   Stores and retrieves text embeddings for efficient similarity search
-   Handles data persistence and state management

### [SummaryGenerator](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/core/SummaryGenerator.py) (src/crawlgpt/core/SummaryGenerator.py)

-   Generates concise summaries of text chunks using Groq API
-   Configurable model selection and parameters
-   Handles empty input validation

### [Database](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/core/database.py) (src/crawl/core/database.py)

-   SQLAlchemy-based database handling for user management and chat history
-   Provides secure user authentication with BCrypt password hashing
-   Manages persistent storage of chat conversations and context  

- Configuration
    - Uses SQLite by default (`sqlite:///crawlgpt.db`)
    - Configurable via DATABASE_URL environment variable
    - Automatic schema creation on startup
    - Session management with SQLAlchemy sessionmaker
- Security Features
    - BCrypt password hashing with PassLib
    - Unique username enforcement
    - Secure session handling
    - Role-based message tracking


## UI Components

### [chat_app.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/ui/chat_app.py) (src/crawlgpt/ui/chat_app.py)

-   Main Streamlit application interface
-   URL processing and content extraction
-   Chat interface with message history
-   System metrics and debug information
-   Import/export functionality

### [chat_ui.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/ui/chat_ui.py)  (src/crawlgpt/ui/chat_ui.py)

-   Development/testing UI with additional debug features
-   Extended metrics visualization
-   Raw data inspection capabilities

## Utilities

### [content_validator.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/utils/content_validator.py) (src/crawlgpt/utils/content_validator.py)

-   URL and content validation
-   MIME type checking
-   Size limit enforcement
-   Security checks for malicious content

### [data_manager.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/utils/data_manager.py) (src/crawlgpt/utils/data_manager.py)

-   Data import/export operations
-   File serialization (JSON/pickle)
-   Timestamped backups
-   State management

### [monitoring.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/utils/monitoring.py) (src/crawlgpt/utils/monitoring.py)

-   Request metrics collection
-   Rate limiting implementation
-   Performance monitoring
-   Usage statistics

### [progress.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/src/crawlgpt/utils/progress.py) (src/crawlgpt/utils/progress.py)

-   Operation progress tracking
-   Status updates
-   Step counting
-   Time tracking

## Testing

### [test_database_handler.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/tests/test_core/test_database_handler.py) (tests/test_core/test_database_handler.py)

-   Tests for vector database operations
-   Integration tests for data storage/retrieval
-   End-to-end flow validation

### [test_integration.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/tests/test_core/test_integration.py) (tests/test_core/test_integration.py)

-   Full system integration tests
-   URL extraction to response generation flow
-   State management validation

### [test_llm_based_crawler.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/tests/test_core/test_llm_based_crawler.py) (tests/test_core/test_llm_based_crawler.py)

-   Crawler functionality tests
-   Content extraction validation
-   Response generation testing

### [test_summary_generator.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/tests/test_core/test_summary_generator.py) (tests/test_core/test_summary_generator.py)

-   Summary generation tests
-   Empty input handling
-   Model output validation

## Configuration

### [pyproject.toml](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/pyproject.toml)

-   Project metadata
-   Dependencies
-   Optional dev dependencies
-   Entry points

### [pytest.ini](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/pytest.ini)

-   Test configuration
-   Path settings
-   Test discovery patterns
-   Reporting options

### [setup_env.py](https://github.com/Jatin-Mehra119/CRAWLGPT/blob/main/setup_env.py)

-   Environment setup script
-   Virtual environment creation
-   Dependency installation
-   Playwright setup

## Features

1.  **Web Crawling**
    
    -   Async web content extraction
    -   Playwright-based rendering
    -   Content validation
    -   Rate limiting
2.  **Content Processing**
    
    -   Text chunking
    -   Vector embeddings
    -   Summarization
    -   Similarity search
3.  **Chat Interface**
    
    -   Message history
    -   Context management
    -   Model parameter control
    -   Debug information
4.  **Data Management**
    
    -   State import/export
    -   Progress tracking
    -   Metrics collection
    -   Error handling
5.  **Testing**
    
    -   Unit tests
    -   Integration tests
    -   Mock implementations
    -   Async test support

## Dependencies

Core:

-   streamlit
-   groq
-   sentence-transformers
-   faiss-cpu
-   crawl4ai
-   pydantic
-   aiohttp
-   beautifulsoup4
-   playwright

Development:

-   pytest
-   pytest-mockito
-   black
-   isort
-   flake8

## License

MIT License
