from langchain_core.embeddings import Embeddings
from vertexai.language_models import TextEmbeddingModel


import logging
from typing import List


class VertexAIEmbeddingsWrapper(Embeddings):
    """Wrapper to make Vertex AI TextEmbeddingModel compatible with LangChain."""

    # Vertex AI gemini-embedding-001 has a limit of 250 texts per request
    BATCH_SIZE = 250

    def __init__(self, model: TextEmbeddingModel):
        self._model = model
        self.model = getattr(model, '_model_id', 'unknown')

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents with automatic batching."""
        try:
            all_embeddings = []

            # Process in batches to avoid API limits
            for i in range(0, len(texts), self.BATCH_SIZE):
                batch = texts[i:i + self.BATCH_SIZE]
                logging.info(f"Embedding batch {i // self.BATCH_SIZE + 1}/{(len(texts) - 1) // self.BATCH_SIZE + 1} ({len(batch)} texts)")
                embeddings = self._model.get_embeddings(texts=batch)
                all_embeddings.extend([e.values for e in embeddings])

            return all_embeddings
        except Exception as e:
            logging.error(f"Error embedding documents: {e}")
            return []

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        try:
            embeddings = self._model.get_embeddings(texts=[text])
            return embeddings[0].values if embeddings else []
        except Exception as e:
            logging.error(f"Error embedding query: {e}")
            return []