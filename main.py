import tiktoken
from productbench.label_augmentation.main import (
    load_data as load_label_data,
    augment_label,
    evaluate_augmentation,
)
from productbench.product_reranking.main import (
    load_data as load_rerank_data,
    rerank_products,
    calculate_ranking_distance,
)
from productbench.ui.app import create_app

def run_benchmarks():
    """Runs the benchmarks and returns the leaderboard data."""
    models = ["model-a", "model-b"]
    leaderboard_data = []

    # Initialize tokenizer with fallback
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Fallback to gpt2 encoding if cl100k_base is not available
        try:
            encoding = tiktoken.get_encoding("gpt2")
        except Exception:
            # Last resort fallback if no tokenizer works
            encoding = None

    def count_tokens(text):
        if encoding:
            return len(encoding.encode(text))
        else:
            # Rough estimation if tokenizer fails
            return len(text) // 4

    for model in models:
        token_count = 0

        # Label Augmentation
        label_data = load_label_data("productbench/data/label_augmentation.json")
        total_score = 0
        for item in label_data:
            augmented_label = augment_label(item["label"])
            # Count tokens for input (label) and output (augmented_label)
            token_count += count_tokens(item["label"]) + count_tokens(augmented_label)
            total_score += evaluate_augmentation(augmented_label, item["ground_truth"])

        avg_score = total_score / len(label_data) if label_data else 0

        # Product Reranking
        rerank_data = load_rerank_data("productbench/data/product_reranking.json")
        total_distance = 0
        for item in rerank_data:
            reranked_products = rerank_products(item["query"], item["products"])

            # Count tokens for input (query + list of products)
            token_count += count_tokens(item["query"])
            for product in item["products"]:
                token_count += count_tokens(product)

            total_distance += calculate_ranking_distance(
                reranked_products, item["ground_truth"]
            )

        avg_distance = total_distance / len(rerank_data) if rerank_data else 0

        cost = 0.0
        score = avg_score

        leaderboard_data.append(
            {
                "model": model,
                "label_augmentation_score": f"{score:.2f}",
                "product_reranking_distance": f"{avg_distance:.2f}",
                "token_count": token_count,
                "estimated_cost": f"{cost:.2f}",
            }
        )
    return leaderboard_data

if __name__ == "__main__":
    leaderboard = run_benchmarks()
    app = create_app(leaderboard)
    app.run(port=5001, debug=True)
