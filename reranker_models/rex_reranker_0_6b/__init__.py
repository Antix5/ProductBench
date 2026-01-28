"""
RexReranker-0.6B Local Reranker Model

A 600M parameter reranker model from thebajajra/RexReranker-0.6B.
Uses a yes/no classification approach with Qwen2 architecture.
"""

from .inference import RexReranker

__all__ = ["RexReranker"]