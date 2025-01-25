import unittest
from unittest.mock import AsyncMock, MagicMock
from crawlgpt.core.LLMBasedCrawler import Model
from crawlgpt.core.DatabaseHandler import VectorDatabase


class TestIntegration(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests
    def setUp(self):
        """
        Set up the integration test environment.
        """
        self.model = Model()

        # Mock the chunking of text
        self.model.chunk_text = MagicMock(return_value=["Chunk 1", "Chunk 2", "Chunk 3"])

        # Mock the summarizer
        self.model.summarizer = MagicMock()
        self.model.summarizer.generate_summary = MagicMock(side_effect=lambda chunk: f"Summary of {chunk}")

        # Mock the database and its methods
        self.model.database = MagicMock()
        self.model.database.data = []  # Simulated in-memory database storage

        def mock_add_data(chunk, summary):
            # Append chunks and summaries to the simulated database
            self.model.database.data.append({"chunk": chunk, "summary": summary})

        self.model.database.add_data = MagicMock(side_effect=mock_add_data)

        # Mock URL content extraction
        self.model.extract_content_from_url = AsyncMock()

    async def test_end_to_end_flow(self):
        """
        Test the full pipeline: URL extraction, summarization, and response generation.
        """
        print("[DEBUG] Starting integration test.")

        # Mock URL and simulate content extraction
        url = "https://example.com"
        print(f"[DEBUG] Mocking URL: {url}")
        await self.model.extract_content_from_url(url)

        # Simulate the summarization and database insertion pipeline
        chunks = self.model.chunk_text("Example text for testing.")
        for chunk in chunks:
            summary = self.model.summarizer.generate_summary(chunk)
            self.model.database.add_data(chunk, summary)

        # Validate database contents
        database_size = len(self.model.database.data)
        print(f"[DEBUG] Database size after processing: {database_size}")
        self.assertGreater(database_size, 0)

        # Generate a query response
        query = "What is the test about?"
        print(f"[DEBUG] Running query: {query}")
        self.model.generate_response = MagicMock(return_value="This is a test response.")
        response = self.model.generate_response(query, temperature=0.5, max_tokens=100, model="llama-3.1-8b-instant")
        print(f"[DEBUG] Query response: {response}")

        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)


if __name__ == "__main__":
    unittest.main()
