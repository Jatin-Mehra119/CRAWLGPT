from groq import Groq
import os

class SummaryGenerator:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=api_key)

    def generate_summary(self, text, model="llama-3.1-8b-instant"):
        messages = [
            {"role": "system", "content": "Generate a concise summary for the following text."},
            {"role": "user", "content": text},
        ]
        completion = self.client.chat.completions.create(
            model=model, messages=messages, temperature=0.7, max_tokens=2500
        )
        return completion.choices[0].message.content.strip()