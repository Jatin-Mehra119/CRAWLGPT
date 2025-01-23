import unittest
from unittest.mock import AsyncMock, MagicMock
from core.LLMBasedCrawler import Model
from core.DatabaseHandler import VectorDatabase


class TestIntegration(unittest.TestCase):
    def setUp(self):
        """
        Set up the integration test environment.
        """
        self.model = Model()
        self.model.chunk_text = MagicMock(return_value=["Chunk 1", "Chunk 2"])
        self.model.summarizer = MagicMock()
        self.model.summarizer.generate_summary = MagicMock(side_effect=lambda chunk: f"Summary of {chunk}")
        self.model.database = VectorDatabase()

    async def test_end_to_end_flow(self):
        """
        Test the full pipeline: URL extraction, summarization, and response generation.
        """
        # Mock URL content extraction
        url = "https://example.com"
        self.model.extract_content_from_url = AsyncMock(return_value=None)

        # Extract content
        await self.model.extract_content_from_url(url)

        # Validate database contents
        self.assertGreater(len(self.model.database.data), 0)

        # Generate a query response
        query = "What is the test about?"
        response = self.model.generate_response(query, temperature=0.5, max_tokens=100, model="llama-3.1-8b-instant")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)


if __name__ == "__main__":
    unittest.main()
