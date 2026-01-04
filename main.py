import json
import re

from productbench.ui.app import create_app


def get_benchmark_results():
    """Reads the benchmark results from BENCHMARK_RESULTS.json and returns the leaderboard data."""
    filepath = "BENCHMARK_RESULTS.json"

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {filepath}.")
        return []

    results = []
    for item in data:
        # Normalize fields for the UI
        model = item.get("model", "Unknown")
        # Handle missing scenario field (backward compatibility)
        scenario = item.get("scenario", "base")
        params_str = item.get("params", "?")

        # Format scores to 4 decimal places string
        aug_score = item.get("aug_score", 0.0)
        rerank_dist = item.get("rerank_dist", 0.0)
        actual_cost = item.get("actual_cost", 0.0)
        avg_aug_cost = item.get("avg_aug_cost", 0.0)
        avg_rerank_cost = item.get("avg_rerank_cost", 0.0)
        time_taken = item.get("time_taken", 0.0)

        label_score_str = f"{aug_score:.4f}"
        rerank_dist_str = f"{rerank_dist:.4f}"
        actual_cost_str = f"${actual_cost:.6f}"
        avg_aug_cost_str = f"${avg_aug_cost:.6f}"
        avg_rerank_cost_str = f"${avg_rerank_cost:.6f}"
        time_taken_str = f"{time_taken:.2f}s"

        token_count = item.get("input_tokens", 0) + item.get("output_tokens", 0)
        note = item.get("note", "")
        details = item.get("details", {})

        # Parse Params to number for chart (if needed, though we use cost for X axis now)
        params_val = 0.0
        match = re.search(r"([\d\.]+)B", params_str)
        if match:
            params_val = float(match.group(1))

        results.append(
            {
                "model": model,
                "scenario": scenario,
                "params": params_str,
                "params_val": params_val,
                "label_augmentation_score": label_score_str,
                "product_reranking_distance": rerank_dist_str,
                "actual_cost": actual_cost,
                "actual_cost_str": actual_cost_str,
                "avg_aug_cost": avg_aug_cost,
                "avg_aug_cost_str": avg_aug_cost_str,
                "avg_rerank_cost": avg_rerank_cost,
                "avg_rerank_cost_str": avg_rerank_cost_str,
                "time_taken": time_taken,
                "time_taken_str": time_taken_str,
                "token_count": token_count,
                "note": note,
                "details": details,
            }
        )

    return results


app = create_app(get_benchmark_results())

if __name__ == "__main__":
    app.run(port=5001, debug=True)
