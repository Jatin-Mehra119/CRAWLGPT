import unittest
from core.DatabaseHandler import VectorDatabase


class TestVectorDatabase(unittest.TestCase):
    def setUp(self):
        self.db = VectorDatabase()
        self.texts = ["This is a test.", "Another test sentence."]
        self.summaries = ["Test summary.", "Another summary."]
        self.db.add_data(self.texts, self.summaries)

    def test_add_data(self):
        self.assertEqual(len(self.db.data), 2)

    def test_search(self):
        results = self.db.search("test", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("summary", results[0])


if __name__ == "__main__":
    unittest.main()
