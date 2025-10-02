"""Vector embedding service"""

import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class VectorService:
    """Service for generating vector embeddings"""

    def __init__(
        self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """Initialize vector service with sentence transformer model

        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy load the sentence transformer model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info(f"Loading sentence transformer model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to vector embeddings

        Args:
            texts: List of text strings to encode

        Returns:
            Array of vector embeddings
        """
        self._load_model()
        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise

    def encode_single(self, text: str) -> List[float]:
        """Encode a single text to vector embedding

        Args:
            text: Text string to encode

        Returns:
            Vector embedding as list of floats
        """
        embeddings = self.encode([text])
        return embeddings[0].tolist()

    def get_dimension(self) -> int:
        """Get the dimension of the vector embeddings

        Returns:
            Dimension of embeddings
        """
        self._load_model()
        # Get dimension by encoding a dummy text
        dummy_embedding = self.encode(["test"])
        return dummy_embedding.shape[1]
