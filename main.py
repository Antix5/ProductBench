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

    for model in models:
        # Label Augmentation
        label_data = load_label_data("productbench/data/label_augmentation.json")
        total_score = sum(
            evaluate_augmentation(augment_label(item["label"]), item["ground_truth"])
            for item in label_data
        )
        avg_score = total_score / len(label_data) if label_data else 0

        # Product Reranking
        rerank_data = load_rerank_data("productbench/data/product_reranking.json")
        total_distance = sum(
            calculate_ranking_distance(
                rerank_products(item["query"], item["products"]), item["ground_truth"]
            )
            for item in rerank_data
        )
        avg_distance = total_distance / len(rerank_data) if rerank_data else 0

        cost = 0.0
        score = avg_score

        leaderboard_data.append(
            {
                "model": model,
                "label_augmentation_score": f"{score:.2f}",
                "product_reranking_distance": f"{avg_distance:.2f}",
                "token_count": 10000,  # Placeholder
                "estimated_cost": f"{cost:.2f}",
            }
        )
    return leaderboard_data

if __name__ == "__main__":
    leaderboard = run_benchmarks()
    app = create_app(leaderboard)
    app.run(port=5001, debug=True)
