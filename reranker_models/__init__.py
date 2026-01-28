"""
Local Reranker Models Package

This package contains local transformer-based reranker models that run on the user's machine.
Each model has its own subdirectory with an inference.py implementing the BaseReranker interface.
"""

import os
import importlib
from typing import List, Type
from .base import BaseReranker


def discover_rerankers() -> List[Type[BaseReranker]]:
    """
    Discover all available reranker models in this package.
    
    Returns:
        List of BaseReranker subclasses found in subdirectories.
    """
    rerankers = []
    package_dir = os.path.dirname(__file__)
    
    # Iterate through subdirectories
    for item in os.listdir(package_dir):
        item_path = os.path.join(package_dir, item)
        
        # Skip non-directories and special files
        if not os.path.isdir(item_path) or item.startswith('_'):
            continue
            
        # Check for inference.py
        inference_path = os.path.join(item_path, 'inference.py')
        if not os.path.exists(inference_path):
            continue
            
        try:
            # Import the module
            module_name = f"reranker_models.{item}.inference"
            module = importlib.import_module(module_name)
            
            # Find the reranker class (assumes one class per module inheriting from BaseReranker)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseReranker) and 
                    attr is not BaseReranker):
                    rerankers.append(attr)
                    break
                    
        except Exception as e:
            print(f"Warning: Failed to load reranker from {item}: {e}")
            continue
    
    return rerankers


def get_reranker(name: str) -> BaseReranker:
    """
    Get a reranker instance by name.
    
    Args:
        name: The name of the reranker (as returned by reranker.name)
        
    Returns:
        Instantiated reranker
        
    Raises:
        ValueError: If reranker not found
    """
    rerankers = discover_rerankers()
    
    for reranker_class in rerankers:
        # Instantiate to get the name
        try:
            instance = reranker_class()
            if instance.name == name:
                return instance
        except Exception:
            # Some models might need resources that aren't available
            # Skip them during discovery
            continue
    
    raise ValueError(f"Reranker '{name}' not found. Available: {[r().name for r in rerankers]}")