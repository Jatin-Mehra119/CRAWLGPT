import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from core.LLMBasedCrawler import Model
from core.DatabaseHandler import VectorDatabase


class TestIntegration(unittest.TestCase):
    def setUp(self):
        """
        Set up the integration test environment.
        """
        self.model = Model()
        self.model.chunk_text = MagicMock(return_value=["Chunk 1", "Chunk 2", "Chunk 3"])
        self.model.summarizer = MagicMock()
        self.model.summarizer.generate_summary = MagicMock(side_effect=lambda chunk: f"Summary of {chunk}")
        self.model.database = VectorDatabase()

    async def async_test_end_to_end_flow(self):
        """
        Test the full pipeline: URL extraction, summarization, and response generation.
        """
        # Debugging: Display the test flow
        print("[DEBUG] Starting end-to-end test.")

        # Mock URL content extraction
        url = "https://example.com"
        print(f"[DEBUG] Mocking content extraction for URL: {url}")
        self.model.extract_content_from_url = AsyncMock(return_value=None)

        # Extract content
        await self.model.extract_content_from_url(url)
        print("[DEBUG] Content extracted successfully.")

        # Simulate adding data to the database
        chunks = self.model.chunk_text("Example text for testing.")
        for chunk in chunks:
            summary = self.model.summarizer.generate_summary(chunk)
            self.model.database.add_data([chunk], [summary])

        # Validate database contents
        database_size = len(self.model.database.data)
        print(f"[DEBUG] Database contains {database_size} entries.")
        self.assertGreater(database_size, 0)

        # Generate a query response
        query = "What is the test about?"
        print(f"[DEBUG] Generating response for query: {query}")
        response = self.model.generate_response(query, temperature=0.5, max_tokens=100, model="llama-3.1-8b-instant")
        print(f"[DEBUG] Query response: {response}")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_end_to_end_flow(self):
        """
        Wrapper to run the asynchronous test using asyncio.run().
        """
        asyncio.run(self.async_test_end_to_end_flow())


if __name__ == "__main__":
    unittest.main()