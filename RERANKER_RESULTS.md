# Local Reranker Benchmark Results

This report contains results for locally-run reranker models.

| Model | Scenario | Params | Device | Rerank Dist | Time (s) | Time/Item (s) | Note |
|---|---|---|---|---|---|---|---|
| RexReranker-0.6B | base | 600M | mps | 0.0556 | 17.16 | 0.2859 |  |
| RexReranker-0.6B | product_type | 600M | mps | 0.0556 | 12.94 | 0.2156 |  |
| RexReranker-0.6B | shelf_category | 600M | mps | 0.0556 | 12.63 | 0.2105 |  |
| product-reranker-mmBERT-small | base | Small | mps:0 | 0.1005 | 5.74 | 0.0957 |  |
| product-reranker-mmBERT-small | product_type | Small | mps:0 | 0.1005 | 1.37 | 0.0229 |  |
| product-reranker-mmBERT-small | shelf_category | Small | mps:0 | 0.1005 | 1.38 | 0.0230 |  |
