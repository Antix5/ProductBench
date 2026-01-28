"""
product-reranker-mmBERT-small Inference Implementation

Based on: https://huggingface.co/Antix5/product-reranker-mmBERT-small

This model uses sentence-transformers CrossEncoder for reranking.
The CrossEncoder ranks documents by relevance to a query.
"""

from typing import List, Tuple
from sentence_transformers import CrossEncoder
from ..base import BaseReranker


class ProductRerankerMmBERTSmall(BaseReranker):
    """
    product-reranker-mmBERT-small implementation for local reranking.
    
    Model: Antix5/product-reranker-mmBERT-small
    Architecture: CrossEncoder (BERT-based)
    """
    
    MODEL_ID = "Antix5/product-reranker-mmBERT-small"
    
    def __init__(self):
        self._model = None
        self._device = None
        
    @property
    def name(self) -> str:
        return "product-reranker-mmBERT-small"
    
    @property
    def params(self) -> str:
        return "Small"
    
    @property
    def device(self) -> str:
        return str(self._device) if self._device else "cpu"
    
    def warmup(self) -> None:
        """Load the CrossEncoder model."""
        print(f"Loading {self.name}...")
        
        # Load the CrossEncoder model
        # It will automatically use the best available device
        self._model = CrossEncoder(self.MODEL_ID)
        
        # Get the device from the underlying model
        if hasattr(self._model, 'device'):
            self._device = self._model.device
        else:
            self._device = "cpu"
        
        print(f"  Using device: {self._device}")
        print(f"  Model loaded successfully!")
    
    def rerank(self, query: str, products: List[str]) -> List[Tuple[int, float]]:
        """
        Rerank products based on relevance to the query.
        
        Args:
            query: The search query string
            products: List of product description strings
            
        Returns:
            List of (index, score) tuples, sorted by relevance (highest score first).
            The index corresponds to the position in the input products list.
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call warmup() first.")
        
        if not products:
            return []
        
        # Use the rank method which returns documents sorted by relevance
        # Returns: [{'corpus_id': idx, 'score': score}, ...]
        results = self._model.rank(query, products)
        
        # Convert to (index, score) tuples, already sorted by score descending
        indexed_scores = [(r['corpus_id'], float(r['score'])) for r in results]
        
        return indexed_scores
    
    def cleanup(self) -> None:
        """Free model resources."""
        if self._model is not None:
            del self._model
            self._model = None
        self._device = None