from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict


class VectorDatabase:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2", dim: int = 384):
        """
        VectorDatabase: A simple vector database for storing and retrieving contextual embeddings.
        """
        self.model = SentenceTransformer(embedding_model_name)
        self.index = faiss.IndexFlatL2(dim)
        self.data = []  # Stores raw data (context and summaries)

    def add_data(self, texts: List[str], summaries: List[str]) -> None:
        """
        Adds data to the vector database.
        Args:
            texts (List[str]): The original texts to be stored.
            summaries (List[str]): Summarized versions of the texts.
        """
        embeddings = self.model.encode(texts)
        self.index.add(np.array(embeddings).astype("float32"))
        for text, summary in zip(texts, summaries):
            self.data.append({"text": text, "summary": summary})

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Searches the vector database for the top-k similar results.
        Args:
            query (str): The query text.
            top_k (int): Number of results to return.
        Returns:
            List[Dict]: List of matched context and summaries.
        """
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype("float32"), top_k)
        results = [self.data[i] for i in indices[0] if i < len(self.data)]
        return results
