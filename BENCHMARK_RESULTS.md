# Benchmark Results

| Model | Params | Cost ($) | Label Aug Score | Rerank Dist | Time (s) | Note |
|---|---|---|---|---|---|---|
| Mistral Small 3 (24B) [Jan 2026] | 24B | $0.000739 | 0.7696 | 0.0120 | 9.65 | Slightly over 20B, but verified in your list and highly capable. |
| Amazon Nova Micro 1.0 | Unknown (Micro) | $0.000777 | 0.7673 | 0.0250 | 8.81 | Amazon's edge model. Worth testing against Granite. |
| Microsoft Phi-4 Multimodal | 14B (Est) | $0.001052 | 0.7667 | 0.0130 | 10.15 | Multimodal version of Phi-4. Good for visual label verification. |
| Mistral Nemo 12B | 12B | $0.000305 | 0.7617 | 0.0363 | 11.15 | Reliable workhorse. Tekken tokenizer is efficient for JSON. |
| Google Gemma 3 12B Instruct | 12B | $0.000757 | 0.7556 | 0.0163 | 16.73 | A new weight class for Gemma. Perfect balance for 16GB VRAM cards. |
| Google Gemma 3 4B Instruct | 4B | $0.000365 | 0.7463 | 0.0385 | 6.92 | New generation 4B. Likely beats older 7B models. |
| Cohere Command R7B (Dec 2024) | 7B | $0.001143 | 0.7437 | 0.0315 | 8.81 | Verified 12-2024 update. Best-in-class citation and tool use. |
| Microsoft Phi-4 | 14B | $0.001511 | 0.7363 | 0.0093 | 29.83 | Latest reasoning model from Microsoft. Pure synthetic data excellence. |
| gemini-2.0-flash-001 | Unknown | $0.002453 | 0.7231 | 0.0063 | 7.60 | Google's Gemini 2 Flash model. Good for comparison with Gemini 3. |
| Mistral Ministral 3B | 3B | $0.000542 | 0.7224 | 0.0896 | 20.68 | Mistral's tiniest edge model. Good baseline. |
| Pixtral 12B | 12B | $0.001628 | 0.7117 | 0.0473 | 10.51 | Vision capable, based on Nemo. Strong generalist. |
| IBM Granite 4.0 Micro | Unknown (Micro) | $0.000412 | 0.6771 | 0.0357 | 13.96 | Enterprise edge model. Good for strict formatting tests. |
| Liquid LFM2 8B | 8B | $0.001172 | 0.6654 | 0.0777 | 8.45 | Liquid Neural Network. Non-transformer architecture. Good wildcard. |
| AllenAI OLMo 3 7B | 7B | $0.001714 | 0.6413 | 0.0789 | 12.34 | Fully open source (data/weights). Great for reproducibility. |
| Qwen 3 14B | 14B | $0.009943 | 0.0000 | 0.0081 | 49.66 | The new 2026 standard. Likely outperforms Qwen 2.5 significantly. |
| GLM-4.1V 9B Thinking | 9B | $0.000312 | 0.0000 | 0.4089 | 14.56 | Explicitly labeled 'Thinking'. Good for complex logic/reranking. |
| Qwen 3 8B | 8B | $0.016320 | 0.0000 | 0.0067 | 379.21 | The smaller sibling of the Qwen 3 14B. |
| NVIDIA Nemotron Nano 9B v2 | 9B | $0.008685 | 0.0000 | 0.0215 | 102.96 | NVIDIA's optimized small model for RAG/Synthetic data. |
