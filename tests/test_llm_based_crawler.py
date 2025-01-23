import unittest
from core.LLMBasedCrawler import Model
from unittest.mock import AsyncMock


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.model.chunk_text = AsyncMock(return_value=["Chunk 1", "Chunk 2"])
        self.model.summarizer.generate_summary = AsyncMock(return_value="Summary")

    async def test_extract_content_from_url(self):
        url = "https://example.com"
        await self.model.extract_content_from_url(url)
        self.assertGreater(len(self.model.database.data), 0)


if __name__ == "__main__":
    unittest.main()
