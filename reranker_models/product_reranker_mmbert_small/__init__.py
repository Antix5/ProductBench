"""
product-reranker-mmBERT-small Local Reranker Model

A CrossEncoder-based reranker model from Antix5/product-reranker-mmBERT-small.
Uses sentence-transformers CrossEncoder architecture.
"""

from .inference import ProductRerankerMmBERTSmall

__all__ = ["ProductRerankerMmBERTSmall"]