import unittest
from unittest.mock import AsyncMock, MagicMock
from core.LLMBasedCrawler import Model


class TestModel(unittest.TestCase):
    def setUp(self):
        """
        Set up the Model instance with mocked dependencies.
        """
        self.model = Model()
        self.model.chunk_text = MagicMock(return_value=["Chunk 1", "Chunk 2"])
        self.model.summarizer = MagicMock()
        self.model.summarizer.generate_summary = MagicMock(side_effect=lambda chunk: f"Summary of {chunk}")
        self.model.database = MagicMock()
        self.model.database.add_data = MagicMock()

    def test_chunk_text(self):
        """
        Test the text chunking functionality.
        """
        text = "This is a long text. It needs to be chunked."
        chunks = self.model.chunk_text(text, chunk_size=10)
        self.assertGreater(len(chunks), 0)

    def test_extract_content_from_url(self):
        """
        Test if content extraction and database storage are successful.
        """
        self.model.extract_content_from_url = AsyncMock(return_value=None)
        url = "https://example.com"
        self.model.database.add_data = MagicMock()
        self.model.summarizer.generate_summary = MagicMock(return_value="Summary of chunk.")

        async def test_crawl():
            await self.model.extract_content_from_url(url)
            self.model.database.add_data.assert_called()

        self.loop.run_until_complete(test_crawl())


if __name__ == "__main__":
    unittest.main()
