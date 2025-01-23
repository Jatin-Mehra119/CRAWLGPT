import os
from groq import Groq
from typing import Dict
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from collections import defaultdict
from .DatabaseHandler import VectorDatabase
from .SummaryGenerator import SummaryGenerator
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#    class OpenAIModelFee(BaseModel):
#        model_name: str = Field(..., description="Name of the OpenAI model.")
#        input_fee: str = Field(..., description="Fee for input token for the OpenAI model.")
#        output_fee: str = Field(..., description="Fee for output token for the OpenAI model.")


class Model:
    """
    A class that represents a model for generating responses based on a given context and query.
    """

    def __init__(self):
        """
        Initializes the Model object, sets up the Groq client, vector database, and summarizer.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=api_key)
        self.context = ""
        self.cache = defaultdict(dict)  # Caching for repeated queries
        self.database = VectorDatabase()  # Initialize the vector database
        self.summarizer = SummaryGenerator()  # Initialize the summarizer

    def chunk_text(self, text: str, chunk_size: int = 5000) -> list:
        """Split text into chunks, respecting code blocks, paragraphs, and sentences."""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            if end >= text_length:
                chunks.append(text[start:].strip())
                break

            chunk = text[start:end]
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

        return chunks

    async def extract_content_from_url(self, url: str):
        """
        Extracts content from a URL using crawl4ai and stores it in the vector database.
        Args:
        - url: The URL to extract content from.
        """
        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(
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

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)
            self.context = result.markdown

        # Split content into chunks
        chunks = self.chunk_text(self.context)
        summaries = [self.summarizer.generate_summary(chunk) for chunk in chunks]

        # Add chunks and summaries to the vector database
        self.database.add_data(chunks, summaries)

    def generate_response(self, query: str, temperature: float, max_tokens: int, model: str, use_summary: bool = True):
        """
        Generates a response based on the given query and retrieves relevant context from the vector database.
        Args:
        - query: The query or question.
        - temperature: The sampling temperature for response generation.
        - max_tokens: The maximum number of tokens for the response.
        - model: The model ID to be used for generating the response.
        - use_summary: Whether to use summarized context or full context.
        Returns:
        - response: The generated response.
        """
        # Retrieve relevant context from the database
        relevant_context = self.database.search(query, top_k=3)
        if use_summary:
            context_summary = "\n".join([item["summary"] for item in relevant_context])
        else:
            context_summary = "\n".join([item["text"] for item in relevant_context])

        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": f"Context: {context_summary}"},
            {"role": "user", "content": f"You are an AI assistant. Answer based on the provided context. If the answer is not in the context, respond with: 'I can't retrieve the answer from the context.'\n{query}"},
        ]

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = completion.choices[0].message.content
            return response
        except Exception as e:
            return f"API request failed: {str(e)}"

    def clear(self):
        """
        Clears the current context and resets the cache.
        """
        self.context = ""
        self.cache.clear()