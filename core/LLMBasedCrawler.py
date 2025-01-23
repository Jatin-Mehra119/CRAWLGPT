import os
from groq import Groq
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from collections import defaultdict
import re
import time
import logging
from dotenv import load_dotenv

# Internal imports
from core.DatabaseHandler import VectorDatabase
from core.SummaryGenerator import SummaryGenerator
from utils.monitoring import MetricsCollector, RateLimiter, Metrics
from utils.progress import ProgressTracker
from utils.data_manager import DataManager
from utils.content_validator import ContentValidator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Model:
    """
    A class that represents a model for generating responses based on a given context and query.
    Includes monitoring, progress tracking, and content validation capabilities.
    """

    def __init__(self, rate_limit_rpm: int = 60):
        """
        Initializes the Model object with all necessary components.
        
        Args:
            rate_limit_rpm (int): Rate limit for requests per minute. Defaults to 60.
        """
        # Initialize API client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=api_key)

        # Core components
        self.context = ""
        self.cache = defaultdict(dict)
        self.database = VectorDatabase()
        self.summarizer = SummaryGenerator()

        # Utility components
        self.metrics_collector = MetricsCollector()
        self.data_manager = DataManager()
        self.content_validator = ContentValidator()
        self.rate_limiter = RateLimiter(requests_per_minute=rate_limit_rpm)

    def chunk_text(self, text: str, chunk_size: int = 5000) -> list:
        """
        Split text into chunks, respecting code blocks, paragraphs, and sentences.
        Maintains original chunking logic while adding progress tracking.
        """
        # Initialize progress tracker
        progress = ProgressTracker(
            total_steps=len(text) // chunk_size + 1,
            operation_name="text_chunking"
        )
        
        chunks = []
        start = 0
        text_length = len(text)
        chunk_count = 0

        while start < text_length:
            chunk_count += 1
            progress.update(chunk_count, f"Processing chunk {chunk_count}")
            
            end = start + chunk_size

            if end >= text_length:
                chunks.append(text[start:].strip())
                break

            chunk = text[start:end]
            # Preserve original boundary detection logic
            code_block = chunk.rfind('```')
            if code_block != -1 and code_block > chunk_size * 0.3:
                end = start + code_block
            elif '\n\n' in chunk:
                last_break = chunk.rfind('\n\n')
                if last_break > chunk_size * 0.3:
                    end = start + last_break
            elif '. ' in chunk:
                last_period = chunk.rfind('. ')
                if last_period > chunk_size * 0.3:
                    end = start + last_period + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = max(start + 1, end)

        progress.complete(f"Successfully created {len(chunks)} chunks")
        return chunks

    async def extract_content_from_url(self, url: str) -> Tuple[bool, str]:
        """
        Extracts content from a URL with progress tracking and validation.
        
        Args:
            url: The URL to extract content from.
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        progress = ProgressTracker(total_steps=5, operation_name="content_extraction")
        start_time = time.time()

        try:
            # Step 1: Validate URL
            progress.update(1, "Validating URL")
            if not self.content_validator.is_valid_url(url):
                raise ValueError("Invalid URL format")

            # Step 2: Check rate limiting
            if not self.rate_limiter.can_proceed():
                raise Exception("Rate limit exceeded. Please try again later.")

            # Step 3: Configure and initialize crawler
            progress.update(2, "Initializing crawler")
            browser_config = BrowserConfig(headless=True)
            crawler_config = self._get_crawler_config()

            # Step 4: Execute crawling
            progress.update(3, "Crawling content")
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=crawler_config)
                self.context = result.markdown

            # Step 5: Validate and process content
            progress.update(4, "Validating content")
            validation_result = self.content_validator.validate_content(self.context)
            if not validation_result["valid"]:
                raise ValueError(f"Content validation failed: {validation_result['reason']}")

            # Step 6: Process content
            progress.update(5, "Processing content")
            chunks = self.chunk_text(self.context)
            summaries = [self.summarizer.generate_summary(chunk) for chunk in chunks]
            self.database.add_data(chunks, summaries)

            # Record success metrics
            self._record_metrics(True, start_time, len(self.context))
            progress.complete("Content successfully extracted and processed")
            return True, "Content extraction completed successfully"

        except Exception as e:
            error_msg = f"Content extraction failed: {str(e)}"
            logger.error(error_msg)
            self._record_metrics(False, start_time, 0)
            progress.fail(error_msg)
            return False, error_msg

    def generate_response(
        self, 
        query: str, 
        temperature: float, 
        max_tokens: int, 
        model: str, 
        use_summary: bool = True
    ) -> str:
        """
        Generates a response with integrated monitoring and rate limiting.
        """
        start_time = time.time()

        try:
            # Check rate limiting
            if not self.rate_limiter.can_proceed():
                return "Rate limit exceeded. Please try again later."

            # Retrieve and prepare context
            relevant_context = self.database.search(query, top_k=3)
            context_items = [item["summary"] if use_summary else item["text"] 
                            for item in relevant_context]
            context_summary = "\n".join(context_items)

            # Generate response
            messages = self._prepare_messages(query, context_summary)
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = completion.choices[0].message.content

            # Record metrics
            self._record_metrics(True, start_time, max_tokens)
            return response

        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            self._record_metrics(False, start_time, 0)
            return error_msg

    def _get_crawler_config(self) -> CrawlerRunConfig:
        """Helper method to create crawler configuration."""
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            page_timeout=80000,
            extraction_strategy=LLMExtractionStrategy(
                provider="ollama",
                api_token=os.getenv("OLLAMA_API_TOKEN"),
                temperature=0,
                top_p=0.9,
                max_tokens=2000
            )
        )

    def _prepare_messages(self, query: str, context: str) -> list:
        """Helper method to prepare messages for the LLM."""
        return [
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": (
                "You are an AI assistant. Answer based on the provided context. "
                "If the answer is not in the context, respond with: "
                "'I can't retrieve the answer from the context.'\n"
                f"{query}"
            )},
        ]

    def _record_metrics(self, success: bool, start_time: float, tokens: int):
        """Helper method to record metrics."""
        self.metrics_collector.record_request(
            success=success,
            response_time=time.time() - start_time,
            tokens_used=tokens
        )

    def clear(self):
        """Clears the current context and resets the cache."""
        self.context = ""
        self.cache.clear()

    def export_current_state(self) -> str:
        """Exports the current state of the model including metrics."""
        return self.data_manager.export_data({
            "metrics": self.metrics_collector.metrics.to_dict(),
            "vector_database": self.database.to_dict()
        }, "model_state")
    
    def import_state(self, state: Dict) -> None:
        """Imports the state of the model including metrics."""
        self.metrics_collector.metrics = Metrics(**state["metrics"])
        self.database.from_dict(state["vector_database"])