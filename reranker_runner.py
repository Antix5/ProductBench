"""
Local Reranker Benchmark Runner

This script benchmarks local transformer-based reranker models.
It follows the same pattern as benchmark_runner.py but for local models.

Usage:
    python reranker_runner.py

Results are saved to RERANKER_RESULTS.json and RERANKER_RESULTS.md.
"""

import json
import time
from typing import Dict, List, Tuple

from reranker_models import discover_rerankers
from productbench.product_reranking.main import load_data, calculate_ranking_distance


# Scenarios to benchmark
SCENARIOS = ['base', 'product_type', 'shelf_category']


def process_rerank_item(reranker, item: dict, context: str = None) -> Tuple[float, float, dict]:
    """
    Process a single reranking item.
    
    Args:
        reranker: The reranker instance
        item: The data item with query, products, ground_truth
        context: Optional context (product_type or shelf_category)
        
    Returns:
        Tuple of (distance, time_taken, detail_dict)
    """
    query = item["query"]
    products = item["products"]
    ground_truth = item["ground_truth"]
    
    # Time the reranking
    start_time = time.time()
    ranked_indices_with_scores = reranker.rerank(query, products)
    end_time = time.time()
    
    # Extract just the indices from the sorted results
    reranked_indices = [idx for idx, score in ranked_indices_with_scores]
    
    # Calculate distance
    distance = calculate_ranking_distance(reranked_indices, ground_truth)
    
    # Time taken for this item
    time_taken = end_time - start_time
    
    detail = {
        "query": query,
        "products": products,
        "reranked_indices": reranked_indices,
        "scores": [round(score, 4) for idx, score in ranked_indices_with_scores],
        "distance": distance,
        "context": context,
        "time": round(time_taken, 4)
    }
    
    return distance, time_taken, detail


def run_reranker_benchmark(reranker_class, rerank_data: List[dict]) -> List[dict]:
    """
    Run benchmark for a single reranker model across all scenarios.
    
    Args:
        reranker_class: The reranker class to instantiate
        rerank_data: The loaded reranking data
        
    Returns:
        List of result dictionaries (one per scenario)
    """
    results = []
    
    # Instantiate and warmup the model
    print(f"\n{'='*60}")
    print(f"Benchmarking: {reranker_class.__name__}")
    print(f"{'='*60}")
    
    try:
        reranker = reranker_class()
        reranker.warmup()
    except Exception as e:
        print(f"  ! Failed to load model: {e}")
        # Return error results for all scenarios
        for scenario in SCENARIOS:
            results.append({
                "model": reranker_class().name if hasattr(reranker_class(), 'name') else reranker_class.__name__,
                "type": "local_reranker",
                "scenario": scenario,
                "params": reranker_class().params if hasattr(reranker_class(), 'params') else "Unknown",
                "device": "error",
                "rerank_dist": 1.0,  # Worst possible distance
                "time_taken": 0,
                "avg_time_per_item": 0,
                "note": f"Error loading model: {str(e)}",
                "details": {}
            })
        return results
    
    # Run each scenario
    for scenario in SCENARIOS:
        print(f"\n  > Scenario: {scenario}")
        start_time = time.time()
        
        distances = []
        times = []
        details = []
        
        try:
            for item in rerank_data:
                context = None
                if scenario == "product_type":
                    context = item.get("product_type")
                elif scenario == "shelf_category":
                    context = item.get("shelf_category")
                
                distance, item_time, detail = process_rerank_item(reranker, item, context)
                distances.append(distance)
                times.append(item_time)
                details.append(detail)
            
            avg_distance = sum(distances) / len(distances) if distances else 1.0
            total_time = time.time() - start_time
            avg_time_per_item = sum(times) / len(times) if times else 0
            
            result = {
                "model": reranker.name,
                "type": "local_reranker",
                "scenario": scenario,
                "params": reranker.params,
                "device": reranker.device,
                "rerank_dist": avg_distance,
                "time_taken": round(total_time, 2),
                "avg_time_per_item": round(avg_time_per_item, 4),
                "note": "",
                "details": {
                    "product_reranking": details
                }
            }
            
            print(f"      > Rerank Dist: {avg_distance:.4f}, Time: {total_time:.2f}s, Avg/Item: {avg_time_per_item:.4f}s")
            
        except Exception as e:
            print(f"      ! Error during benchmarking: {e}")
            result = {
                "model": reranker.name,
                "type": "local_reranker",
                "scenario": scenario,
                "params": reranker.params,
                "device": reranker.device,
                "rerank_dist": 1.0,
                "time_taken": 0,
                "avg_time_per_item": 0,
                "note": f"Error: {str(e)}",
                "details": {}
            }
        
        results.append(result)
    
    # Cleanup
    try:
        reranker.cleanup()
    except Exception as e:
        print(f"  ! Warning: cleanup failed: {e}")
    
    return results


def main():
    """Main entry point."""
    print("Local Reranker Benchmark Runner")
    print("=" * 60)
    
    # Load data
    print("\nLoading reranking data...")
    rerank_data = load_data("productbench/data/product_reranking.json")
    print(f"  Loaded {len(rerank_data)} items")
    
    # Discover available rerankers
    print("\nDiscovering reranker models...")
    reranker_classes = discover_rerankers()
    print(f"  Found {len(reranker_classes)} model(s)")
    
    if not reranker_classes:
        print("\nNo reranker models found. Make sure models are in reranker_models/ directory.")
        return
    
    # Load existing results
    print("\nLoading existing results...")
    try:
        with open("RERANKER_RESULTS.json", "r") as f:
            existing_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_results = []
    
    print(f"  Found {len(existing_results)} existing result(s)")
    
    # Map existing results by (model, scenario)
    results_map: Dict[Tuple[str, str], dict] = {}
    for res in existing_results:
        key = (res.get("model"), res.get("scenario"))
        results_map[key] = res
    
    # Determine which benchmarks need to be run
    all_results = []
    
    for reranker_class in reranker_classes:
        # Get the model name (need to instantiate to get name)
        try:
            temp_instance = reranker_class()
            model_name = temp_instance.name
            del temp_instance
        except Exception as e:
            print(f"\n! Failed to get name from {reranker_class.__name__}: {e}")
            continue
        
        # Check which scenarios are missing
        missing_scenarios = []
        for scenario in SCENARIOS:
            key = (model_name, scenario)
            if key not in results_map:
                missing_scenarios.append(scenario)
        
        if not missing_scenarios:
            print(f"\nSkipping {model_name} - All scenarios already benchmarked.")
            # Add existing results to final list
            for scenario in SCENARIOS:
                key = (model_name, scenario)
                if key in results_map:
                    all_results.append(results_map[key])
            continue
        
        print(f"\n{model_name}: Running {len(missing_scenarios)} missing scenario(s): {', '.join(missing_scenarios)}")
        
        # Run the benchmark
        new_results = run_reranker_benchmark(reranker_class, rerank_data)
        
        # Update results map with new results
        for res in new_results:
            key = (res["model"], res["scenario"])
            results_map[key] = res
    
    # Convert map back to list
    final_results = list(results_map.values())
    
    # Sort by model name, then scenario
    scenario_order = {s: i for i, s in enumerate(SCENARIOS)}
    final_results.sort(key=lambda x: (x["model"], scenario_order.get(x.get("scenario", "base"), 999)))
    
    # Generate Markdown Report
    markdown_output = "# Local Reranker Benchmark Results\n\n"
    markdown_output += "This report contains results for locally-run reranker models.\n\n"
    markdown_output += "| Model | Scenario | Params | Device | Rerank Dist | Time (s) | Time/Item (s) | Note |\n"
    markdown_output += "|---|---|---|---|---|---|---|---|\n"
    
    for res in final_results:
        note = res.get("note", "")
        markdown_output += f"| {res['model']} | {res.get('scenario', 'base')} | {res['params']} | {res['device']} | {res.get('rerank_dist', 0):.4f} | {res.get('time_taken', 0):.2f} | {res.get('avg_time_per_item', 0):.4f} | {note} |\n"
    
    with open("RERANKER_RESULTS.md", "w") as f:
        f.write(markdown_output)
    
    # Save JSON Report
    with open("RERANKER_RESULTS.json", "w") as f:
        json.dump(final_results, f, indent=4)
    
    print("\n" + "=" * 60)
    print("Benchmark completed!")
    print(f"  - Results saved to RERANKER_RESULTS.json")
    print(f"  - Report saved to RERANKER_RESULTS.md")
    print(f"  - Total results: {len(final_results)}")


if __name__ == "__main__":
    main()