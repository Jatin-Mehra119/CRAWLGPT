import unittest
from crawlgpt.core.SummaryGenerator import SummaryGenerator


class TestSummaryGenerator(unittest.TestCase):
    def setUp(self):
        """
        Set up the SummaryGenerator instance.
        """
        self.summarizer = SummaryGenerator()

    def test_generate_summary(self):
        """
        Test if the summarizer generates valid summaries.
        """
        text = "This is a simple test text for summarization."
        print(f"[DEBUG] Summarizing text: {text}")
        summary = self.summarizer.generate_summary(text)
        print(f"[DEBUG] Generated summary: {summary}")
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)

    def test_empty_text(self):
        """
        Test how the summarizer handles empty input.
        """
        text = ""
        print("[DEBUG] Testing summarization on empty input.")
        summary = self.summarizer.generate_summary(text)
        print(f"[DEBUG] Summary for empty input: {summary}")
        self.assertEqual(summary, "")


if __name__ == "__main__":
    unittest.main()
