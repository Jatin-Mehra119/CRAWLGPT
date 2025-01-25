# CrawlGPT Documentation

## Overview

CrawlGPT is a web content crawler with GPT-powered summarization and chat capabilities. It extracts content from URLs, stores it in a vector database, and enables natural language querying of the stored content.

## Project Structure

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
├── .gitignore
├── LICENSE
├── README.md
├── Docs
├── pyproject.toml
├── pytest.ini
└── setup_env.py
```

## Core Components

### LLMBasedCrawler (src/crawlgpt/core/LLMBasedCrawler.py)

-   Main crawler class handling web content extraction and processing
-   Integrates with Groq API for language model operations
-   Manages content chunking, summarization and response generation
-   Includes rate limiting and metrics collection

### DatabaseHandler (src/crawlgpt/core/DatabaseHandler.py)

-   Vector database implementation using FAISS
-   Stores and retrieves text embeddings for efficient similarity search
-   Handles data persistence and state management

### SummaryGenerator (src/crawlgpt/core/SummaryGenerator.py)

-   Generates concise summaries of text chunks using Groq API
-   Configurable model selection and parameters
-   Handles empty input validation

## UI Components

### [chat_app.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)  (src/crawlgpt/ui/chat_app.py)

-   Main Streamlit application interface
-   URL processing and content extraction
-   Chat interface with message history
-   System metrics and debug information
-   Import/export functionality

### [chat_ui.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)  (src/crawlgpt/ui/chat_ui.py)

-   Development/testing UI with additional debug features
-   Extended metrics visualization
-   Raw data inspection capabilities

## Utilities

### [content_validator.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   URL and content validation
-   MIME type checking
-   Size limit enforcement
-   Security checks for malicious content

### [data_manager.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Data import/export operations
-   File serialization (JSON/pickle)
-   Timestamped backups
-   State management

### [monitoring.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Request metrics collection
-   Rate limiting implementation
-   Performance monitoring
-   Usage statistics

### [progress.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Operation progress tracking
-   Status updates
-   Step counting
-   Time tracking

## Testing

### [test_database_handler.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Tests for vector database operations
-   Integration tests for data storage/retrieval
-   End-to-end flow validation

### [test_integration.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Full system integration tests
-   URL extraction to response generation flow
-   State management validation

### [test_llm_based_crawler.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Crawler functionality tests
-   Content extraction validation
-   Response generation testing

### [test_summary_generator.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Summary generation tests
-   Empty input handling
-   Model output validation

## Configuration

### [pyproject.toml](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Project metadata
-   Dependencies
-   Optional dev dependencies
-   Entry points

### [pytest.ini](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

-   Test configuration
-   Path settings
-   Test discovery patterns
-   Reporting options

### [setup_env.py](https://orange-memory-g4xp5wqvqvr4hrvx.github.dev/?folder=%2Fworkspaces%2FCRAWLGPT)

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