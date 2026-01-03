import os
import json
import asyncio
import tiktoken
import time
import math
from openai import AsyncOpenAI, OpenAIError
from productbench.label_augmentation.main import load_data as load_label_data
from productbench.product_reranking.main import load_data as load_rerank_data, calculate_ranking_distance

# List of models to benchmark

MODELS = [
    # --- 🌟 The "Next-Gen" Frontier ---
    {
        "model": "Qwen 3 14B",
        "openrouter_id": "qwen/qwen3-14b",
        "params": "14B",
        "note": "The new 2026 standard. Likely outperforms Qwen 2.5 significantly."
    },
    {
        "model": "Microsoft Phi-4",
        "openrouter_id": "microsoft/phi-4",
        "params": "14B",
        "note": "Latest reasoning model from Microsoft. Pure synthetic data excellence."
    },
    {
        "model": "Google Gemma 3 12B Instruct",
        "openrouter_id": "google/gemma-3-12b-it",
        "params": "12B",
        "note": "A new weight class for Gemma. Perfect balance for 16GB VRAM cards."
    },
    # --- 🧠 Specialized Reasoning & "Thinking" Models ---
    {
        "model": "GLM-4.1V 9B Thinking",
        "openrouter_id": "thudm/glm-4.1v-9b-thinking",
        "params": "9B",
        "note": "Explicitly labeled 'Thinking'. Good for complex logic/reranking."
    },

    # --- 🛠️ Tool Use & Agent Specialists ---
    {
        "model": "Cohere Command R7B (Dec 2024)",
        "openrouter_id": "cohere/command-r7b-12-2024",
        "params": "7B",
        "note": "Verified 12-2024 update. Best-in-class citation and tool use."
    },
    {
        "model": "Mistral Nemo 12B",
        "openrouter_id": "mistralai/mistral-nemo",
        "params": "12B",
        "note": "Reliable workhorse. Tekken tokenizer is efficient for JSON."
    },
    {
        "model": "Mistral Small 3 (24B) [Jan 2026]",
        "openrouter_id": "mistralai/mistral-small-24b-instruct-2501",
        "params": "24B",
        "note": "Slightly over 20B, but verified in your list and highly capable."
    },

    # --- ⚡ High Efficiency Edge Models (<10B) ---
    {
        "model": "Google Gemma 3 4B Instruct",
        "openrouter_id": "google/gemma-3-4b-it",
        "params": "4B",
        "note": "New generation 4B. Likely beats older 7B models."
    },
    {
        "model": "Qwen 3 8B",
        "openrouter_id": "qwen/qwen3-8b",
        "params": "8B",
        "note": "The smaller sibling of the Qwen 3 14B."
    },
    {
        "model": "IBM Granite 4.0 Micro",
        "openrouter_id": "ibm-granite/granite-4.0-h-micro",
        "params": "Unknown (Micro)",
        "note": "Enterprise edge model. Good for strict formatting tests."
    },
    {
        "model": "Mistral Ministral 3B",
        "openrouter_id": "mistralai/ministral-3b",
        "params": "3B",
        "note": "Mistral's tiniest edge model. Good baseline."
    },
    {
        "model": "NVIDIA Nemotron Nano 9B v2",
        "openrouter_id": "nvidia/nemotron-nano-9b-v2",
        "params": "9B",
        "note": "NVIDIA's optimized small model for RAG/Synthetic data."
    },

    # --- 👁️ Multimodal & Novel Architectures ---
    {
        "model": "Pixtral 12B",
        "openrouter_id": "mistralai/pixtral-12b",
        "params": "12B",
        "note": "Vision capable, based on Nemo. Strong generalist."
    },
    {
        "model": "Liquid LFM2 8B",
        "openrouter_id": "liquid/lfm2-8b-a1b",
        "params": "8B",
        "note": "Liquid Neural Network. Non-transformer architecture. Good wildcard."
    },
    {
        "model": "Microsoft Phi-4 Multimodal",
        "openrouter_id": "microsoft/phi-4-multimodal-instruct",
        "params": "14B (Est)",
        "note": "Multimodal version of Phi-4. Good for visual label verification."
    },
    {
        "model" : "gemini-2.0-flash-001",
        "openrouter_id": "google/gemini-2.0-flash-001",
        "params": "Unknown",
        "note": "Google's Gemini 2 Flash model. Good for comparison with Gemini 3."
    },

    # --- 🌍 Open & Multilingual ---
    {
        "model": "AllenAI OLMo 3 7B",
        "openrouter_id": "allenai/olmo-3-7b-instruct",
        "params": "7B",
        "note": "Fully open source (data/weights). Great for reproducibility."
    },
    {
        "model": "Amazon Nova Micro 1.0",
        "openrouter_id": "amazon/nova-micro-v1",
        "params": "Unknown (Micro)",
        "note": "Amazon's edge model. Worth testing against Granite."
    }
]



# Semaphore to limit concurrent requests
CONCURRENCY_LIMIT = 20
EVAL_MODEL = "google/gemini-3-flash-preview"

# Load pricing map
PRICING_MAP = {}
try:
    with open("pricing_map.json", "r") as f:
        PRICING_MAP = json.load(f)
except FileNotFoundError:
    print("Warning: pricing_map.json not found. Prices will be 0.")

# --- Async Helper Functions (copied and adapted from libraries) ---

async def augment_label_async(client: AsyncOpenAI, label: str, model: str) -> tuple[str, str, int, int]:
    """Uses an LLM to augment the product label (Async). Returns (content, raw_output, prompt_tokens, completion_tokens)."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that improves product labels. Your goal is to make the label more descriptive and human-readable, expanding abbreviations and adding missing context if possible."},
                {"role": "user", "content": f"Augment this product label, output nothing else: '{label}'"}
            ],
            temperature=0.3,
            max_tokens=60
        )
        content = response.choices[0].message.content.strip()

        prompt_tokens = 0
        completion_tokens = 0
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

        return content, content, prompt_tokens, completion_tokens
    except Exception as e:
        # print(f"Error calling OpenAI API (augment): {e}")
        return f"Augmented: {label} (Error)", str(e), 0, 0

async def evaluate_augmentation_async(client: AsyncOpenAI, augmented_label: str, ground_truth: str, model: str) -> float:
    """Evaluates the quality of the augmented label (Async)."""
    if "Augmented:" in augmented_label and "(Error)" in augmented_label:
         return 0.0

    try:
        prompt = (
            f"Compare the augmented label with the ground truth label.\n"
            f"Augmented Label: {augmented_label}\n"
            f"Ground Truth: {ground_truth}\n"
            f"Rate the semantic similarity and correctness on a scale from 0.0 to 1.0, "
            f"where 1.0 means they are identical in meaning and 0.0 means they are completely unrelated.\n"
            f"Return ONLY the numeric score."
        )

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that evaluates semantic similarity."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=10
        )

        content = response.choices[0].message.content.strip()
        try:
            score = float(content)
            return max(0.0, min(1.0, score))
        except ValueError:
            pass
    except Exception as e:
        # print(f"LLM evaluation failed: {e}")
        pass

    # Fallback: Token overlap (Jaccard Similarity)
    aug_tokens = set(augmented_label.lower().split())
    gt_tokens = set(ground_truth.lower().split())

    if not aug_tokens or not gt_tokens:
        return 0.0

    intersection = aug_tokens.intersection(gt_tokens)
    union = aug_tokens.union(gt_tokens)
    return len(intersection) / len(union)

async def rerank_products_async(client: AsyncOpenAI, query: str, products: list, model: str) -> tuple[list, str, int, int]:
    """Reranks products using an LLM (Async). Returns (indices, raw_output, prompt_tokens, completion_tokens)."""
    products_formatted = "\n".join([f"{i}: {p}" for i, p in enumerate(products)])

    prompt = f"""
    You are a search ranking expert.
    Query: "{query}"

    Products:
    {products_formatted}

    Rank the products above based on their relevance to the query.
    Return the result as a JSON list of integers, representing the indices of the products in descending order of relevance.
    Do not include any explanation, just the JSON list.
    Example output: [1, 0, 3, 2]
    """

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that ranks products."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        original_content = content

        prompt_tokens = 0
        completion_tokens = 0
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

        # Clean potential markdown code blocks
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
             content = content.replace("```", "")

        # Try to extract JSON list if there's extra text
        if "[" in content and "]" in content:
            start = content.find("[")
            end = content.rfind("]") + 1
            content = content[start:end]

        try:
            ranked_indices = json.loads(content)
            if isinstance(ranked_indices, list) and all(isinstance(i, int) for i in ranked_indices):
                valid_indices = [i for i in ranked_indices if 0 <= i < len(products)]
                existing_set = set(valid_indices)
                for i in range(len(products)):
                    if i not in existing_set:
                        valid_indices.append(i)
                return valid_indices, original_content, prompt_tokens, completion_tokens
            else:
                return list(range(len(products))), original_content, prompt_tokens, completion_tokens
        except json.JSONDecodeError:
             return list(range(len(products))), original_content, prompt_tokens, completion_tokens

    except Exception as e:
        # print(f"Error calling OpenAI API (rerank): {e}")
        return list(range(len(products))), str(e), 0, 0

async def check_model_health_async(client: AsyncOpenAI, model_id: str) -> bool:
    """Checks if the model is available (Async)."""
    print(f"  Checking health of {model_id}...")
    try:
        await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
            timeout=10
        )
        return True
    except Exception as e:
        print(f"  ! Model {model_id} health check failed: {e}")
        return False

# --- Main Benchmark Logic ---

async def process_label_item(sem, client, item, model_id, eval_model):
    """Process a single label augmentation item."""
    async with sem:
        augmented_label, raw_output, p_tokens, c_tokens = await augment_label_async(client, item["label"], model_id)
        score = await evaluate_augmentation_async(client, augmented_label, item["ground_truth"], eval_model)
        # Note: We are NOT counting tokens for evaluation in the model cost, only the model's generation cost.

        detail = {
            "input": item["label"],
            "ground_truth": item["ground_truth"],
            "output": augmented_label,
            "raw_output": raw_output,
            "score": score
        }
        return score, p_tokens, c_tokens, detail

async def process_rerank_item(sem, client, item, model_id):
    """Process a single product reranking item."""
    async with sem:
        reranked_indices, raw_output, p_tokens, c_tokens = await rerank_products_async(client, item["query"], item["products"], model_id)
        distance = calculate_ranking_distance(reranked_indices, item["ground_truth"])

        detail = {
            "query": item["query"],
            "products": item["products"],
            "reranked_indices": reranked_indices,
            "raw_output": raw_output,
            "distance": distance
        }

        return distance, p_tokens, c_tokens, detail

async def run_benchmarks_async():
    openrouter_key = os.environ.get("OPENROUTER_KEY")
    if not openrouter_key:
        print("Error: OPENROUTER_KEY environment variable not set.")
        return

    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key,
    )

    results = []
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    print(f"Starting ASYNC benchmarks for {len(MODELS)} models...")
    print(f"Using evaluation model: {EVAL_MODEL}")
    print(f"Concurrency Limit: {CONCURRENCY_LIMIT}")

    # Load data once
    label_data = load_label_data("productbench/data/label_augmentation.json")
    rerank_data = load_rerank_data("productbench/data/product_reranking.json")

    for model_info in MODELS:
        model_name = model_info["model"]
        model_id = model_info["openrouter_id"]
        params = model_info["params"]

        # Get Pricing
        price_data = PRICING_MAP.get(model_id, {"input": 0.0, "output": 0.0})
        input_price_per_m = price_data.get("input", 0.0)
        output_price_per_m = price_data.get("output", 0.0)

        print(f"\nBenchmarking: {model_name} ({model_id})")

        start_time = time.time()

        try: # Safety net for the entire model process
            # Health Check
            is_healthy = await check_model_health_async(client, model_id)
            if not is_healthy:
                print(f"Skipping {model_name} due to health check failure.")
                results.append({
                    "model": model_name,
                    "id": model_id,
                    "params": params,
                    "price_input": input_price_per_m,
                    "price_output": output_price_per_m,
                    "aug_score": 0.0,
                    "rerank_dist": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "actual_cost": 0.0,
                    "time_taken": 0,
                    "note": "Skipped (Unavailable)",
                    "details": {}
                })
                continue

            # --- Label Augmentation ---
            print(f"  - Running Label Augmentation ({len(label_data)} items)...")
            label_tasks = [
                process_label_item(sem, client, item, model_id, EVAL_MODEL)
                for item in label_data
            ]
            label_results = await asyncio.gather(*label_tasks)

            total_aug_score = sum(r[0] for r in label_results)
            total_aug_p_tokens = sum(r[1] for r in label_results)
            total_aug_c_tokens = sum(r[2] for r in label_results)
            label_details = [r[3] for r in label_results]
            avg_aug_score = total_aug_score / len(label_data) if label_data else 0

            # --- Product Reranking ---
            print(f"  - Running Product Reranking ({len(rerank_data)} items)...")
            rerank_tasks = [
                process_rerank_item(sem, client, item, model_id)
                for item in rerank_data
            ]
            rerank_results = await asyncio.gather(*rerank_tasks)

            total_rerank_dist = sum(r[0] for r in rerank_results)
            total_rerank_p_tokens = sum(r[1] for r in rerank_results)
            total_rerank_c_tokens = sum(r[2] for r in rerank_results)
            rerank_details = [r[3] for r in rerank_results]
            avg_rerank_dist = total_rerank_dist / len(rerank_data) if rerank_data else 0

            total_input_tokens = total_aug_p_tokens + total_rerank_p_tokens
            total_output_tokens = total_aug_c_tokens + total_rerank_c_tokens

            # Calculate Actual Cost
            # Price is per 1M tokens.
            cost_input = (total_input_tokens / 1_000_000) * input_price_per_m
            cost_output = (total_output_tokens / 1_000_000) * output_price_per_m
            actual_cost = cost_input + cost_output

            end_time = time.time()
            time_taken = end_time - start_time

            results.append({
                "model": model_name,
                "id": model_id,
                "params": params,
                "price_input": input_price_per_m,
                "price_output": output_price_per_m,
                "aug_score": avg_aug_score,
                "rerank_dist": avg_rerank_dist,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "actual_cost": actual_cost,
                "time_taken": time_taken,
                "note": model_info.get("note", ""),
                "details": {
                    "label_augmentation": label_details,
                    "product_reranking": rerank_details
                }
            })

            print(f"    > Aug Score: {avg_aug_score:.4f}, Rerank Dist: {avg_rerank_dist:.4f}, Time: {time_taken:.2f}s, Cost: ${actual_cost:.6f}")

        except Exception as e:
            print(f"CRITICAL ERROR benchmarking {model_name}: {e}")
            results.append({
                "model": model_name,
                "id": model_id,
                "params": params,
                "price_input": input_price_per_m,
                "price_output": output_price_per_m,
                "aug_score": 0.0,
                "rerank_dist": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "actual_cost": 0.0,
                "time_taken": 0,
                "note": f"Error: {str(e)}",
                "details": {}
            })
            continue

    # Sort results
    results.sort(key=lambda x: x["aug_score"], reverse=True)

    # Generate Markdown Report
    markdown_output = "# Benchmark Results\n\n"
    markdown_output += "| Model | Params | Cost ($) | Label Aug Score | Rerank Dist | Time (s) | Note |\n"
    markdown_output += "|---|---|---|---|---|---|---|\n"

    for res in results:
        note = res.get("note", "")
        markdown_output += f"| {res['model']} | {res['params']} | ${res['actual_cost']:.6f} | {res['aug_score']:.4f} | {res['rerank_dist']:.4f} | {res['time_taken']:.2f} | {note} |\n"

    with open("BENCHMARK_RESULTS.md", "w") as f:
        f.write(markdown_output)

    # Save JSON Report
    with open("BENCHMARK_RESULTS.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\nBenchmark completed. Results saved to BENCHMARK_RESULTS.md and BENCHMARK_RESULTS.json")

if __name__ == "__main__":
    asyncio.run(run_benchmarks_async())
