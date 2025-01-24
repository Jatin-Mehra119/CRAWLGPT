from groq import Groq
import os

class SummaryGenerator:
    """
    A class for generating concise summaries of text using the Groq API.
    
    This class handles text summarization using language models through 
    the Groq API service. It requires a valid GROQ_API_KEY environment variable.
    
    Attributes:
        client (Groq): Initialized Groq API client
        
    Examples:
        >>> generator = SummaryGenerator()
        >>> text = "This is a long piece of text that needs summarizing."
        >>> summary = generator.generate_summary(text)
        >>> print(summary)
        'A concise summary of the text.'
    
    Raises:
        ValueError: If GROQ_API_KEY environment variable is not set
    """
    def __init__(self):
        """
        Initialize the SummaryGenerator with Groq API client.
        
        Raises:
            ValueError: If GROQ_API_KEY environment variable is not set
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.client = Groq(api_key=api_key)

    def generate_summary(self, text, model="llama-3.1-8b-instant"):
        """
        Generate a concise summary of the provided text.
        
        Args:
            text (str): The text to summarize
            model (str, optional): The model to use for summarization. 
                                 Defaults to "llama-3.1-8b-instant"
        
        Returns:
            str: Generated summary of the input text
            
        Examples:
            >>> generator = SummaryGenerator()
            >>> text = "This is a detailed text about AI technology..."
            >>> summary = generator.generate_summary(text)
            >>> print(summary)
            'A concise overview of AI technology.'
            
        Raises:
            Exception: If API call fails or text processing errors occur
        """
        messages = [
            {"role": "system", "content": "Generate a concise summary for the following text."},
            {"role": "user", "content": text},
        ]
        completion = self.client.chat.completions.create(
            model=model, messages=messages, temperature=0.7, max_tokens=2500
        )
        return completion.choices[0].message.content.strip()