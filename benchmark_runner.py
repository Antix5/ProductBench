import os
import json
import tiktoken
from openai import OpenAI
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

# List of models to benchmark
MODELS = [
    # --- The "Must Benchmark" Frontier (Latest Releases) ---
    {
        "model": "Ministral 3 14B (Dec 2025 Release)",
        "openrouter_id": "mistralai/ministral-14b-2512",
        "params": "14B",
    },
    {
        "model": "Microsoft Phi-4",
        "openrouter_id": "microsoft/phi-4",
        "params": "14B",
    },
    {
        "model": "DeepSeek R1 Distill Qwen 14B",
        "openrouter_id": "deepseek/deepseek-r1-distill-qwen-14b",
        "params": "14B",
    },
    {
        "model": "Qwen 2.5 14B Instruct",
        "openrouter_id": "qwen/qwen-2.5-14b-instruct",
        "params": "14B",
    },

    # --- The Granite Family (IBM Enterprise) ---
    {
        "model": "Granite 3.0 8B Instruct",
        "openrouter_id": "ibm/granite-3.0-8b-instruct",
        "params": "8B",
    },
    {
        "model": "Granite 4.0 Micro (3B)",
        "openrouter_id": "ibm-granite/granite-4.0-h-micro",
        "params": "3B",
    },

    # --- Tool Use & RAG Specialists ---
    {
        "model": "Cohere Command R7B (12-2024)",
        "openrouter_id": "cohere/command-r7b-12-2024",
        "params": "7B",
    },
    {
        "model": "Mistral Nemo 12B",
        "openrouter_id": "mistralai/mistral-nemo",
        "params": "12B",
    },
    {
        "model": "GLM-4 9B Chat",
        "openrouter_id": "thudm/glm-4-9b-chat",
        "params": "9B",
    },

    # --- High Knowledge & Creative Generalists ---
    {
        "model": "Gemma 2 9B Instruct",
        "openrouter_id": "google/gemma-2-9b-it",
        "params": "9B",
    },
    {
        "model": "Yi 1.5 9B Chat",
        "openrouter_id": "01-ai/yi-1.5-9b-chat",
        "params": "9B",
    },
    {
        "model": "InternLM 2.5 20B Chat",
        "openrouter_id": "internlm/internlm-2.5-20b-chat",
        "params": "20B",
    },

    # --- Efficient & Multilingual (<10B) ---
    {
        "model": "Aya Expanse 8B",
        "openrouter_id": "cohere/aya-expanse-8b",
        "params": "8B",
    },
    {
        "model": "Qwen 2.5 7B Instruct",
        "openrouter_id": "qwen/qwen-2.5-7b-instruct",
        "params": "7B",
    },
    {
        "model": "Microsoft Phi-3.5 Mini",
        "openrouter_id": "microsoft/phi-3.5-mini-128k-instruct",
        "params": "3.8B",
    },
    {
        "model": "Solar 10.7B Instruct",
        "openrouter_id": "upstage/solar-10.7b-instruct-v1",
        "params": "10.7B",
    },

    # --- Unique Architectures (MoE / Vision) ---
    {
        "model": "DeepSeek V2 Lite Chat",
        "openrouter_id": "deepseek/deepseek-v2-lite-chat",
        "params": "16B (MoE)",
    },
    {
        "model": "Pixtral 12B",
        "openrouter_id": "mistralai/pixtral-12b",
        "params": "12B",
    },
    {
        "model": "Mistral 7B Instruct v0.3",
        "openrouter_id": "mistralai/mistral-7b-instruct-v0.3",
        "params": "7B",
    },
    {
        "model": "NVIDIA Nemotron-4 4B Instruct",
        "openrouter_id": "nvidia/nemotron-4-mini-instruct",
        "params": "4B",
    }
]

def run_benchmarks():
    openrouter_key = os.environ.get("OPENROUTER_KEY")
    if not openrouter_key:
        print("Error: OPENROUTER_KEY environment variable not set.")
        return

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key,
    )

    # Model used for evaluation (judge)
    EVAL_MODEL = "google/gemini-3-flash-preview"

    # Initialize tokenizer
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        try:
            encoding = tiktoken.get_encoding("gpt2")
        except Exception:
            encoding = None

    def count_tokens(text):
        if encoding:
            return len(encoding.encode(text))
        else:
            return len(text) // 4

    results = []

    print(f"Starting benchmarks for {len(MODELS)} models...")
    print(f"Using evaluation model: {EVAL_MODEL}")

    for model_info in MODELS:
        model_name = model_info["model"]
        model_id = model_info["openrouter_id"]
        params = model_info["params"]

        print(f"\nBenchmarking: {model_name} ({model_id})")

        token_count = 0

        # --- Label Augmentation ---
        print("  - Running Label Augmentation...")
        try:
            label_data = load_label_data("productbench/data/label_augmentation.json")
            total_score = 0
            for item in label_data:
                # Augment using the benchmark model
                augmented_label = augment_label(item["label"], model=model_id, client=client)
                token_count += count_tokens(item["label"]) + count_tokens(augmented_label)

                # Evaluate using the judge model (Gemini 3 Flash Preview)
                score = evaluate_augmentation(augmented_label, item["ground_truth"], model=EVAL_MODEL, client=client)
                total_score += score

            avg_aug_score = total_score / len(label_data) if label_data else 0
        except Exception as e:
            print(f"  ! Error in Label Augmentation: {e}")
            avg_aug_score = 0

        # --- Product Reranking ---
        print("  - Running Product Reranking...")
        try:
            rerank_data = load_rerank_data("productbench/data/product_reranking.json")
            total_distance = 0
            for item in rerank_data:
                # Rerank using the benchmark model
                reranked_indices = rerank_products(item["query"], item["products"], model=model_id, client=client)

                token_count += count_tokens(item["query"])
                for product in item["products"]:
                    token_count += count_tokens(product)

                total_distance += calculate_ranking_distance(
                    reranked_indices, item["ground_truth"]
                )

            avg_rerank_dist = total_distance / len(rerank_data) if rerank_data else 0
        except Exception as e:
            print(f"  ! Error in Product Reranking: {e}")
            avg_rerank_dist = 0 # Worst case

        results.append({
            "model": model_name,
            "id": model_id,
            "params": params,
            "aug_score": avg_aug_score,
            "rerank_dist": avg_rerank_dist,
            "tokens": token_count
        })

    # Generate Markdown Report
    markdown_output = "# Benchmark Results\n\n"
    markdown_output += "| Model | Params | Label Augmentation Score | Product Reranking Distance | Token Count |\n"
    markdown_output += "|---|---|---|---|---|\n"

    for res in results:
        markdown_output += f"| {res['model']} | {res['params']} | {res['aug_score']:.4f} | {res['rerank_dist']:.4f} | {res['tokens']} |\n"

    with open("BENCHMARK_RESULTS.md", "w") as f:
        f.write(markdown_output)

    print("\nBenchmark completed. Results saved to BENCHMARK_RESULTS.md")

if __name__ == "__main__":
    run_benchmarks()
