"""
Base class for local reranker models.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class BaseReranker(ABC):
    """
    Abstract base class for local reranker models.
    
    All reranker implementations must inherit from this class and implement
    the abstract methods.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable name of the reranker model.
        
        Returns:
            String name (e.g., "RexReranker-0.6B")
        """
        pass
    
    @property
    @abstractmethod
    def params(self) -> str:
        """
        Model size/parameters description.
        
        Returns:
            String like "600M" or "7B"
        """
        pass
    
    @property
    def device(self) -> str:
        """
        Device being used for inference.
        
        Returns:
            String like "cuda", "mps", "cpu"
        """
        return "cpu"
    
    @abstractmethod
    def warmup(self) -> None:
        """
        Load the model into memory and prepare for inference.
        
        This should be called once before running benchmarks.
        """
        pass
    
    @abstractmethod
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
        pass
    
    def cleanup(self) -> None:
        """
        Optional cleanup method to free resources.
        
        Called after benchmarking is complete.
        """
        pass