"""
RexReranker-0.6B Inference Implementation

Based on: https://huggingface.co/thebajajra/RexReranker-0.6B

This model uses a yes/no classification approach where:
- The model is given a query and document
- It outputs "yes" or "no" to indicate relevance
- The logits for yes/no are converted to a probability score
"""

import torch
from typing import List, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer
from ..base import BaseReranker


class RexReranker(BaseReranker):
    """
    RexReranker-0.6B implementation for local reranking.
    
    Model: thebajajra/RexReranker-0.6B
    Architecture: Qwen2-based causal LM with yes/no classification
    """
    
    MODEL_ID = "thebajajra/RexReranker-0.6B"
    MAX_LENGTH = 8192
    BATCH_SIZE = 4  # Process products in batches for efficiency
    
    def __init__(self):
        self._tokenizer = None
        self._model = None
        self._device = None
        self._prefix_tokens = None
        self._suffix_tokens = None
        self._token_true_id = None
        self._token_false_id = None
        
    @property
    def name(self) -> str:
        return "RexReranker-0.6B"
    
    @property
    def params(self) -> str:
        return "600M"
    
    @property
    def device(self) -> str:
        return str(self._device) if self._device else "cpu"
    
    def _get_device(self) -> torch.device:
        """Determine the best available device."""
        if torch.backends.mps.is_available():
            return torch.device("mps")
        elif torch.cuda.is_available():
            return torch.device("cuda")
        else:
            return torch.device("cpu")
    
    def warmup(self) -> None:
        """Load the model and tokenizer."""
        print(f"Loading {self.name}...")
        
        self._device = self._get_device()
        print(f"  Using device: {self._device}")
        
        # Load tokenizer with left padding (required for this model)
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_ID,
            padding_side='left',
            trust_remote_code=True
        )
        
        # Determine dtype based on device
        if self._device.type == "cuda":
            dtype = torch.float16
        elif self._device.type == "mps":
            # MPS works better with float32 for some models
            dtype = torch.float16 if torch.backends.mps.is_available() else torch.float32
        else:
            dtype = torch.float32
        
        # Load model
        self._model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_ID,
            torch_dtype=dtype,
            trust_remote_code=True
        ).to(self._device).eval()
        
        # Setup special tokens
        self._token_false_id = self._tokenizer.convert_tokens_to_ids("no")
        self._token_true_id = self._tokenizer.convert_tokens_to_ids("yes")
        
        # Setup prefix/suffix for formatting
        prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        
        self._prefix_tokens = self._tokenizer.encode(prefix, add_special_tokens=False)
        self._suffix_tokens = self._tokenizer.encode(suffix, add_special_tokens=False)
        
        print(f"  Model loaded successfully!")
    
    def _format_instruction(self, query: str, doc: str, instruction: str = None) -> str:
        """Format the query-document pair for the model."""
        if instruction is None:
            instruction = 'Given a web search query, retrieve relevant passages that answer the query'
        
        return f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}"
    
    def _process_inputs(self, pairs: List[str]) -> dict:
        """Tokenize and prepare inputs for the model."""
        # First pass: tokenize without padding to find lengths
        inputs = self._tokenizer(
            pairs,
            padding=False,
            truncation='longest_first',
            return_attention_mask=False,
            max_length=self.MAX_LENGTH - len(self._prefix_tokens) - len(self._suffix_tokens)
        )
        
        # Add prefix and suffix tokens
        for i, input_ids in enumerate(inputs['input_ids']):
            inputs['input_ids'][i] = self._prefix_tokens + input_ids + self._suffix_tokens
        
        # Pad to batch
        inputs = self._tokenizer.pad(
            inputs,
            padding=True,
            return_tensors="pt",
            max_length=self.MAX_LENGTH
        )
        
        # Move to device
        for key in inputs:
            inputs[key] = inputs[key].to(self._device)
        
        return inputs
    
    @torch.no_grad()
    def _compute_scores(self, inputs: dict) -> List[float]:
        """Compute relevance scores from model logits."""
        # Get model outputs
        outputs = self._model(**inputs)
        
        # Get logits for the last token position
        batch_scores = outputs.logits[:, -1, :]
        
        # Extract yes/no logits
        true_vector = batch_scores[:, self._token_true_id]
        false_vector = batch_scores[:, self._token_false_id]
        
        # Stack and apply log softmax
        batch_scores = torch.stack([false_vector, true_vector], dim=1)
        batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
        
        # Return "yes" probability as the relevance score
        scores = batch_scores[:, 1].exp().tolist()
        return scores
    
    def _score_batch(self, query: str, products: List[str]) -> List[float]:
        """Score a batch of products against a query."""
        # Format all query-product pairs
        pairs = [self._format_instruction(query, product) for product in products]
        
        # Prepare inputs
        inputs = self._process_inputs(pairs)
        
        # Compute scores
        scores = self._compute_scores(inputs)
        
        return scores
    
    def rerank(self, query: str, products: List[str]) -> List[Tuple[int, float]]:
        """
        Rerank products based on relevance to the query.
        
        Args:
            query: The search query string
            products: List of product description strings
            
        Returns:
            List of (index, score) tuples, sorted by relevance (highest score first)
        """
        if self._model is None or self._tokenizer is None:
            raise RuntimeError("Model not loaded. Call warmup() first.")
        
        if not products:
            return []
        
        # Score all products in batches
        all_scores = []
        for i in range(0, len(products), self.BATCH_SIZE):
            batch = products[i:i + self.BATCH_SIZE]
            batch_scores = self._score_batch(query, batch)
            all_scores.extend(batch_scores)
        
        # Create (index, score) pairs and sort by score descending
        indexed_scores = [(i, score) for i, score in enumerate(all_scores)]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        
        return indexed_scores
    
    def cleanup(self) -> None:
        """Free model resources."""
        if self._model is not None:
            del self._model
            self._model = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        
        # Clear GPU cache if applicable
        if self._device and self._device.type == "cuda":
            torch.cuda.empty_cache()
        
        self._device = None