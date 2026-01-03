import os
import json
import asyncio
import tiktoken
import math
from openai import AsyncOpenAI, OpenAIError
from productbench.label_augmentation.main import load_data as load_label_data
from productbench.product_reranking.main import load_data as load_rerank_data, calculate_ranking_distance

# List of models to benchmark

MODELS = [
    # --- 🌟 The "Next-Gen" Frontier (Verified from your screenshots) ---
    {
        "model": "Qwen 3 14B",
        "openrouter_id": "qwen/qwen3-14b",  # From Image 5
        "params": "14B",
        "note": "The new 2026 standard. Likely outperforms Qwen 2.5 significantly."
    },
    {
        "model": "Microsoft Phi-4",
        "openrouter_id": "microsoft/phi-4",  # From Image 5
        "params": "14B",  # Estimated based on Phi series (usually 14B for mid-size)
        "note": "Latest reasoning model from Microsoft. Pure synthetic data excellence."
    },
    {
        "model": "Google Gemma 3 12B Instruct",
        "openrouter_id": "google/gemma-3-12b-it",  # From Image 2
        "params": "12B",
        "note": "A new weight class for Gemma. Perfect balance for 16GB VRAM cards."
    },
    # --- 🧠 Specialized Reasoning & "Thinking" Models ---
    {
        "model": "GLM-4.1V 9B Thinking",
        "openrouter_id": "thudm/glm-4.1v-9b-thinking",  # From Image 3
        "params": "9B",
        "note": "Explicitly labeled 'Thinking'. Good for complex logic/reranking."
    },

    # --- 🛠️ Tool Use & Agent Specialists ---
    {
        "model": "Cohere Command R7B (Dec 2024)",
        "openrouter_id": "cohere/command-r7b-12-2024",  # From Image 3
        "params": "7B",
        "note": "Verified 12-2024 update. Best-in-class citation and tool use."
    },
    {
        "model": "Mistral Nemo 12B",
        "openrouter_id": "mistralai/mistral-nemo",  # From Image 1
        "params": "12B",
        "note": "Reliable workhorse. Tekken tokenizer is efficient for JSON."
    },
    {
        "model": "Mistral Small 3 (24B) [Jan 2026]",
        "openrouter_id": "mistralai/mistral-small-24b-instruct-2501",  # From Image 2
        "params": "24B",
        "note": "Slightly over 20B, but verified in your list and highly capable."
    },

    # --- ⚡ High Efficiency Edge Models (<10B) ---
    {
        "model": "Google Gemma 3 4B Instruct",
        "openrouter_id": "google/gemma-3-4b-it",  # From Image 1
        "params": "4B",
        "note": "New generation 4B. Likely beats older 7B models."
    },
    {
        "model": "Qwen 3 8B",
        "openrouter_id": "qwen/qwen3-8b",  # From Image 3
        "params": "8B",
        "note": "The smaller sibling of the Qwen 3 14B."
    },
    {
        "model": "IBM Granite 4.0 Micro",
        "openrouter_id": "ibm-granite/granite-4.0-h-micro",  # From Image 1
        "params": "Unknown (Micro)",
        "note": "Enterprise edge model. Good for strict formatting tests."
    },
    {
        "model": "Mistral Ministral 3B",
        "openrouter_id": "mistralai/ministral-3b",  # From Image 3
        "params": "3B",
        "note": "Mistral's tiniest edge model. Good baseline."
    },
    {
        "model": "NVIDIA Nemotron Nano 9B v2",
        "openrouter_id": "nvidia/nemotron-nano-9b-v2",  # From Image 4
        "params": "9B",
        "note": "NVIDIA's optimized small model for RAG/Synthetic data."
    },

    # --- 👁️ Multimodal & Novel Architectures ---
    {
        "model": "Pixtral 12B",
        "openrouter_id": "mistralai/pixtral-12b",  # From Image 7
        "params": "12B",
        "note": "Vision capable, based on Nemo. Strong generalist."
    },
    {
        "model": "Liquid LFM2 8B",
        "openrouter_id": "liquid/lfm2-8b-a1b",  # From Image 4
        "params": "8B",
        "note": "Liquid Neural Network. Non-transformer architecture. Good wildcard."
    },
    {
        "model": "Microsoft Phi-4 Multimodal",
        "openrouter_id": "microsoft/phi-4-multimodal-instruct",  # From Image 4
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
        "openrouter_id": "allenai/olmo-3-7b-instruct",  # From Image 7
        "params": "7B",
        "note": "Fully open source (data/weights). Great for reproducibility."
    },
    {
        "model": "Amazon Nova Micro 1.0",
        "openrouter_id": "amazon/nova-micro-v1",  # From Image 3
        "params": "Unknown (Micro)",
        "note": "Amazon's edge model. Worth testing against Granite."
    }
]



# Semaphore to limit concurrent requests
CONCURRENCY_LIMIT = 20
EVAL_MODEL = "google/gemini-3-flash-preview"

# --- Async Helper Functions (copied and adapted from libraries) ---

async def augment_label_async(client: AsyncOpenAI, label: str, model: str) -> str:
    """Uses an LLM to augment the product label (Async)."""
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        # print(f"Error calling OpenAI API (augment): {e}")
        return f"Augmented: {label} (Error)"

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

async def rerank_products_async(client: AsyncOpenAI, query: str, products: list, model: str) -> list:
    """Reranks products using an LLM (Async)."""
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

        ranked_indices = json.loads(content)

        if isinstance(ranked_indices, list) and all(isinstance(i, int) for i in ranked_indices):
            valid_indices = [i for i in ranked_indices if 0 <= i < len(products)]
            existing_set = set(valid_indices)
            for i in range(len(products)):
                if i not in existing_set:
                    valid_indices.append(i)
            return valid_indices
        else:
            return list(range(len(products)))

    except Exception as e:
        # print(f"Error calling OpenAI API (rerank): {e}")
        return list(range(len(products)))

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

async def process_label_item(sem, client, item, model_id, eval_model, count_tokens_func):
    """Process a single label augmentation item."""
    async with sem:
        augmented_label = await augment_label_async(client, item["label"], model_id)
        score = await evaluate_augmentation_async(client, augmented_label, item["ground_truth"], eval_model)
        tokens = count_tokens_func(item["label"]) + count_tokens_func(augmented_label)
        return score, tokens

async def process_rerank_item(sem, client, item, model_id, count_tokens_func):
    """Process a single product reranking item."""
    async with sem:
        reranked_indices = await rerank_products_async(client, item["query"], item["products"], model_id)
        distance = calculate_ranking_distance(reranked_indices, item["ground_truth"])

        t_count = count_tokens_func(item["query"])
        for product in item["products"]:
            t_count += count_tokens_func(product)

        return distance, t_count

async def run_benchmarks_async():
    openrouter_key = os.environ.get("OPENROUTER_KEY")
    if not openrouter_key:
        print("Error: OPENROUTER_KEY environment variable not set.")
        return

    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key,
    )

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

        print(f"\nBenchmarking: {model_name} ({model_id})")

        # Health Check
        is_healthy = await check_model_health_async(client, model_id)
        if not is_healthy:
            print(f"Skipping {model_name} due to health check failure.")
            results.append({
                "model": model_name,
                "id": model_id,
                "params": params,
                "aug_score": 0.0,
                "rerank_dist": 0.0,
                "tokens": 0,
                "note": "Skipped (Unavailable)"
            })
            continue

        # --- Label Augmentation ---
        print(f"  - Running Label Augmentation ({len(label_data)} items)...")
        label_tasks = [
            process_label_item(sem, client, item, model_id, EVAL_MODEL, count_tokens)
            for item in label_data
        ]
        label_results = await asyncio.gather(*label_tasks)

        total_aug_score = sum(r[0] for r in label_results)
        total_aug_tokens = sum(r[1] for r in label_results)
        avg_aug_score = total_aug_score / len(label_data) if label_data else 0

        # --- Product Reranking ---
        print(f"  - Running Product Reranking ({len(rerank_data)} items)...")
        rerank_tasks = [
            process_rerank_item(sem, client, item, model_id, count_tokens)
            for item in rerank_data
        ]
        rerank_results = await asyncio.gather(*rerank_tasks)

        total_rerank_dist = sum(r[0] for r in rerank_results)
        total_rerank_tokens = sum(r[1] for r in rerank_results)
        avg_rerank_dist = total_rerank_dist / len(rerank_data) if rerank_data else 0

        total_tokens = total_aug_tokens + total_rerank_tokens

        results.append({
            "model": model_name,
            "id": model_id,
            "params": params,
            "aug_score": avg_aug_score,
            "rerank_dist": avg_rerank_dist,
            "tokens": total_tokens
        })

        print(f"    > Aug Score: {avg_aug_score:.4f}, Rerank Dist: {avg_rerank_dist:.4f}")

    # Generate Markdown Report
    markdown_output = "# Benchmark Results\n\n"
    markdown_output += "| Model | Params | Label Augmentation Score | Product Reranking Distance | Token Count | Note |\n"
    markdown_output += "|---|---|---|---|---|---|\n"

    for res in results:
        note = res.get("note", "")
        markdown_output += f"| {res['model']} | {res['params']} | {res['aug_score']:.4f} | {res['rerank_dist']:.4f} | {res['tokens']} | {note} |\n"

    with open("BENCHMARK_RESULTS.md", "w") as f:
        f.write(markdown_output)

    # Save JSON Report
    with open("BENCHMARK_RESULTS.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\nBenchmark completed. Results saved to BENCHMARK_RESULTS.md and BENCHMARK_RESULTS.json")

if __name__ == "__main__":
    asyncio.run(run_benchmarks_async())
