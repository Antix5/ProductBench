import asyncio
import json
import os
import re
import time

from openai import AsyncOpenAI

from productbench.label_augmentation.main import load_data as load_label_data
from productbench.product_reranking.main import calculate_ranking_distance
from productbench.product_reranking.main import load_data as load_rerank_data

# List of models to benchmark

MODELS = [
    {
        "model": "Mimo V2 Flash",
        "openrouter_id": "xiaomi/mimo-v2-flash:free",
        "params": "300B",
        "note": "",
    },
    {
        "model": "Deepseek V3.2",
        "openrouter_id": "deepseek/deepseek-v3.2",
        "params": "600B",
        "note": "",
    },
    {
        "model": "Kimi k2 0905",
        "openrouter_id": "moonshotai/kimi-k2-0905",
        "params": "1T",
        "note": "",
    },
    {
        "model": "Microsoft Phi-4",
        "openrouter_id": "microsoft/phi-4",
        "params": "14B",
        "note": "",
    },
    {
        "model": "Google Gemma 3 12B Instruct",
        "openrouter_id": "google/gemma-3-12b-it",
        "params": "12B",
        "note": "",
    },
    {
        "model": "Cohere Command R7B",
        "openrouter_id": "cohere/command-r7b-12-2024",
        "params": "7B",
        "note": "",
    },
    {
        "model": "Mistral Nemo 12B",
        "openrouter_id": "mistralai/mistral-nemo",
        "params": "12B",
        "note": "",
    },
    {
        "model": "Mistral Small 3",
        "openrouter_id": "mistralai/mistral-small-24b-instruct-2501",
        "params": "24B",
        "note": "",
    },
    {
        "model": "Google Gemma 3 4B Instruct",
        "openrouter_id": "google/gemma-3-4b-it",
        "params": "4B",
        "note": "",
    },
    {
        "model": "Mistral Ministral 3B",
        "openrouter_id": "mistralai/ministral-3b",
        "params": "3B",
        "note": "",
    },
    {
        "model": "Ministral 14B 2512",
        "openrouter_id": "mistralai/ministral-14b-2512",
        "params": "14B",
        "note": "",
    },
    {
        "model": "Ministral 8B 2512",
        "openrouter_id": "mistralai/ministral-8b-2512",
        "params": "14B",
        "note": "",
    },
    {
        "model": "Ministral 3B 2512",
        "openrouter_id": "mistralai/ministral-3b-2512",
        "params": "14B",
        "note": "",
    },
    {
        "model": "Mistral Large 3 2512",
        "openrouter_id": "mistralai/mistral-large-2512",
        "params": "675B MOE",
        "note": "",
    },
    {
        "model": "Gemini 2.0 flash",
        "openrouter_id": "google/gemini-2.0-flash-001",
        "params": "Unknown",
        "note": "Google's Gemini 2 Flash model. Reference model",
    },
    {
        "model": "Gemini 3 flash (Judge)",
        "openrouter_id": "google/gemini-3-flash-preview",
        "params": "Unknown",
        "note": "This model is here to see how the judge model self evaluate.",
    },
    {
        "model": "Gemini 2.5 Flash lite",
        "openrouter_id": "google/gemini-2.5-flash-lite",
        "params": "Unknown",
        "note": "",
    },
    {
        "model": "Amazon Nova Micro 1.0",
        "openrouter_id": "amazon/nova-micro-v1",
        "params": "Unknown (Micro)",
        "note": "",
    },
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


def extract_content_and_reasoning(response):
    """
    Extracts content and potential reasoning from an OpenAI/OpenRouter response object.
    Handles 'reasoning', 'reasoning_content', and refusals.
    """
    message = response.choices[0].message
    content = message.content

    # Check for refusal
    if getattr(message, "refusal", None):
        return None, f"REFUSAL: {message.refusal}"

    # Handle None content (sometimes happens with pure reasoning models or tool calls)
    if content is None:
        content = ""

    raw_dump = f"Content: {content}\n"

    # Try to find reasoning
    reasoning = None
    if hasattr(message, "reasoning") and message.reasoning:
        reasoning = message.reasoning
    elif hasattr(message, "reasoning_content") and message.reasoning_content:
        reasoning = message.reasoning_content
    # OpenRouter sometimes puts it in extra_fields or directly on the object if using standard OpenAI lib
    # but the python lib maps known fields.

    if reasoning:
        raw_dump += f"\n--- Reasoning ---\n{reasoning}\n-----------------"

    return content, raw_dump


async def augment_label_async(
    client: AsyncOpenAI, label: str, model: str, context: str = None
) -> tuple[str, str, int, int]:
    """Uses an LLM to augment the product label (Async). Returns (content, raw_output, prompt_tokens, completion_tokens)."""
    try:
        user_content = f"""Analyze the input label and output a clean, generic product description.

            Strict Rules:
            1. **Identify the Category:** You MUST convert the input into its generic product type (e.g., 'iPhone 13' -> 'Smartphone', 'Air Jordan' -> 'Basketball Shoes').
            2. **Remove Brand Names:** Do not include the manufacturer or brand name (e.g., remove 'Samsung', 'Nike', 'Apple', 'Sony') unless it is essential to describe the object type (e.g., 'Jeep').
            3. **Keep Key Specs:** Retain important technical details (e.g., '5G', '128GB', 'Wireless', 'Men\'s').
            4. **No Fluff:** Remove marketing words ('Promo', 'Best', 'Sale').
            5. **Output:** Return ONLY the cleaned descriptive string between <response> and </response> tags
            Examples:
            Input: 'SAM GAL S21 5G 128GB PROMO!!'
            Output: <response>5G Smartphone 128GB</response>

            Input: 'NK Air Zoom Pegasus 38 M - RUN'
            Output: <response>Men's Running Shoes</response>

            Input: 'PXL 5 GOOGLE 128'
            Output: <response>Smartphone 128GB</response>

            Input: '{label}'
            Output:"""

        if context:
             user_content = f"Product Context: {context}\n\n" + user_content

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert E-commerce Query Normalizer. Your task is to extract the core product category and technical specifications from a label, removing specific commercial branding.""",
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            temperature=0.3,
            max_tokens=200,  # Increased slightly to allow for some reasoning if needed, though we ask for nothing else
            extra_body={
                "include_reasoning": False
            },  # Request reasoning for supported models
        )

        content, raw_dump = extract_content_and_reasoning(response)

        prompt_tokens = 0
        completion_tokens = 0
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

        if not content and not raw_dump:
            return (
                "",
                "Empty Response Object",
                prompt_tokens,
                completion_tokens,
            )

        # If content is empty but we have reasoning, maybe the model thought the reasoning was the answer?
        # Or it just failed to output content.
        if not content.strip():  # pyright: ignore[reportOptionalMemberAccess]
            return (
                "",
                raw_dump,
                prompt_tokens,
                completion_tokens,
            )

        # Use regex to extract content between <response> tags
        content_str = str(content) if content is not None else ""

        match = re.search(r"<response>(.*?)</response>", content_str, re.DOTALL)
        if match:
            content = match.group(1).strip()
        else:
            # Model didn't use response tags, return empty string for automatic 0 score
            return "", raw_dump, prompt_tokens, completion_tokens

        return content.strip(), raw_dump, prompt_tokens, completion_tokens  # pyright: ignore[reportOptionalMemberAccess]

    except Exception as e:
        # print(f"Error calling OpenAI API (augment): {e}")
        return f"Augmented: {label} (Error)", str(e), 0, 0


async def evaluate_augmentation_async(
    client: AsyncOpenAI,
    source_label: str,
    augmented_label: str,
    ground_truth: str,
    model: str,
) -> float:
    """Evaluates the quality of the augmented label (Async)."""
    if len(augmented_label) == 0:
        return 0.0

    try:
        prompt = f"""
            You are an expert Search Relevance Evaluator for a Retrieval-Augmented Generation (RAG) system. Your task is to rate the quality of an "Augmented Label" by comparing it to a "Ground Truth" label, using the "Source Label" for context.

            ### Input Data
            * **Source Label:** {source_label} (The original raw query)
            * **Augmented Label:** {augmented_label} (The generated expansion/normalization)
            * **Ground Truth:** {ground_truth} (The expected correct category or intent)

            ### Evaluation Criteria
            Score the semantic similarity and correctness on a scale from 0.0 to 1.0 based on the following rules:

            1.  **Core Meaning (Highest Priority):** The Augmented Label must match the intent and category of the Ground Truth.
            2.  **Brand/Entity Constraints:**
                * **Bad:** If the Ground Truth is a generic category (e.g., "smartphone") and the Augmented Label contains ONLY a specific brand or commercial name (e.g., "Pixel 5"), penalize the score heavily (near 0.0).
                * **Good:** Specific brands are allowed ONLY if the generic product type is also present (e.g., "Pixel 5 smartphone" is acceptable).
            3.  **No Fluff:** The Augmented Label should not contain marketing buzzwords (e.g., "Best," "Amazing," "Cheap") or unnecessary filler words.
            4.  **Language Agnostic:** Ignore language differences; focus purely on semantic meaning.

            ### Scoring Rubric
            * **1.0 (Perfect):** The Augmented Label conveys the exact same meaning as the Ground Truth, matches the category, and contains no fluff.
            * **0.5 (Partial):** The Augmented Label captures the general meaning but misses the specific product category (e.g., listing a brand name without the product type) or includes minor fluff.
            * **0.0 (Fail):** The Augmented Label is unrelated, misleading, purely a specific commercial name without a category (when GT is a category), or uses heavy marketing language.

            ### Output
            Return **ONLY** the numeric score (e.g., 0.8). Do not add explanations or text.
        """

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=10,
        )

        content = response.choices[0].message.content.strip()  # pyright: ignore[reportOptionalMemberAccess]
        try:
            score = float(content)
            return max(0.0, min(1.0, score))
        except ValueError:
            pass
    except Exception:
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


async def rerank_products_async(
    client: AsyncOpenAI, query: str, products: list, model: str, context: str = None
) -> tuple[list, str, int, int]:
    """Reranks products using an LLM (Async). Returns (indices, raw_output, prompt_tokens, completion_tokens)."""
    products_formatted = "\n".join([f"{i}: {p}" for i, p in enumerate(products)])

    prompt = f"""
    You are a search ranking expert.
    Query: "{query}"

    Products:
    {products_formatted}

    Rank the products above based on their relevance to the query.
    Return the result as a JSON list of integers between <response> and </response> tags, representing the indices of the products in descending order of relevance.
    Do not include any explanation, just the JSON list.
    Example output: <response>[1, 0, 3, 2]</response>
    """

    if context:
        prompt = f"Product Context: {context}\n\n" + prompt

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that ranks products.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            extra_body={"include_reasoning": False},
        )

        content, raw_dump = extract_content_and_reasoning(response)
        original_content = raw_dump  # Store the full dump for debugging

        prompt_tokens = 0
        completion_tokens = 0
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

        if not content:
            return (
                list(range(len(products))),
                original_content,
                prompt_tokens,
                completion_tokens,
            )

        # Use regex to extract content between <response> tags
        content_str = str(content) if content is not None else ""
        match = re.search(r"<response>(.*?)</response>", content_str, re.DOTALL)
        if match:
            content = match.group(1).strip()

        # Clean potential markdown code blocks
        clean_content = content
        if "```json" in clean_content:
            clean_content = clean_content.replace("```json", "").replace("```", "")
        elif "```" in clean_content:
            clean_content = clean_content.replace("```", "")

        # Try to extract JSON list if there's extra text
        if "[" in clean_content and "]" in clean_content:
            start = clean_content.find("[")
            end = clean_content.rfind("]") + 1
            clean_content = clean_content[start:end]

        try:
            ranked_indices = json.loads(clean_content)
            if isinstance(ranked_indices, list) and all(
                isinstance(i, int) for i in ranked_indices
            ):
                valid_indices = [i for i in ranked_indices if 0 <= i < len(products)]
                existing_set = set(valid_indices)
                for i in range(len(products)):
                    if i not in existing_set:
                        valid_indices.append(i)
                return valid_indices, original_content, prompt_tokens, completion_tokens
            else:
                return (
                    list(range(len(products))),
                    original_content,
                    prompt_tokens,
                    completion_tokens,
                )
        except json.JSONDecodeError:
            return (
                list(range(len(products))),
                original_content,
                prompt_tokens,
                completion_tokens,
            )

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
            max_tokens=16,
            timeout=10,
        )
        return True
    except Exception as e:
        print(f"  ! Model {model_id} health check failed: {e}")
        return False


# --- Main Benchmark Logic ---


async def process_label_item(sem, client, item, model_id, eval_model, context=None):
    """Process a single label augmentation item."""
    async with sem:
        augmented_label, raw_output, p_tokens, c_tokens = await augment_label_async(
            client, item["label"], model_id, context=context
        )
        score = await evaluate_augmentation_async(
            client, item["label"], augmented_label, item["ground_truth"], eval_model
        )
        # Note: We are NOT counting tokens for evaluation in the model cost, only the model's generation cost.

        detail = {
            "input": item["label"],
            "ground_truth": item["ground_truth"],
            "output": augmented_label,
            "raw_output": raw_output,
            "score": score,
            "context": context
        }
        return score, p_tokens, c_tokens, detail


async def process_rerank_item(sem, client, item, model_id, context=None):
    """Process a single product reranking item."""
    async with sem:
        reranked_indices, raw_output, p_tokens, c_tokens = await rerank_products_async(
            client, item["query"], item["products"], model_id, context=context
        )
        distance = calculate_ranking_distance(reranked_indices, item["ground_truth"])

        detail = {
            "query": item["query"],
            "products": item["products"],
            "reranked_indices": reranked_indices,
            "raw_output": raw_output,
            "distance": distance,
            "context": context
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

    # Load existing results if available
    try:
        with open("BENCHMARK_RESULTS.json", "r") as f:
            existing_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_results = []

    # Map existing results by (model_id, scenario) for easy lookup/update
    # Note: Using model_id (OpenRouter ID) as unique key + scenario
    results_map = {}
    for res in existing_results:
        # Backward compatibility for old results without scenario
        scen = res.get("scenario", "base")
        key = (res.get("id"), scen)
        results_map[key] = res

    # Load data once
    label_data = load_label_data("productbench/data/label_augmentation.json")
    rerank_data = load_rerank_data("productbench/data/product_reranking.json")

    SCENARIOS = ['base', 'product_type', 'shelf_category']

    for model_info in MODELS:
        model_name = model_info["model"]
        model_id = model_info["openrouter_id"]
        params = model_info["params"]

        # Determine which scenarios are missing for this model
        scenarios_to_run = []
        for scenario in SCENARIOS:
            if (model_id, scenario) not in results_map:
                scenarios_to_run.append(scenario)

        if not scenarios_to_run:
            print(f"Skipping {model_name} ({model_id}) - All scenarios already benchmarked.")
            continue

        # Get Pricing
        price_data = PRICING_MAP.get(model_id, {"input": 0.0, "output": 0.0})
        input_price_per_m = price_data.get("input", 0.0)
        output_price_per_m = price_data.get("output", 0.0)

        print(f"\nBenchmarking: {model_name} ({model_id})")
        print(f"  > Missing scenarios: {', '.join(scenarios_to_run)}")

        try:  # Safety net for the entire model process
            # Health Check
            is_healthy = await check_model_health_async(client, model_id)
            if not is_healthy:
                print(f"Skipping {model_name} due to health check failure.")
                # Add skipped result for all MISSING scenarios
                for scenario in scenarios_to_run:
                    results.append(
                        {
                            "model": model_name,
                            "id": model_id,
                            "scenario": scenario,
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
                            "details": {},
                        }
                    )
                continue

            for scenario in scenarios_to_run:
                print(f"  > Scenario: {scenario}")
                start_time = time.time()

                # --- Label Augmentation ---
                print(f"    - Running Label Augmentation ({len(label_data)} items)...")
                label_tasks = []
                for item in label_data:
                    context = None
                    if scenario == "product_type":
                        context = item.get("product_type")
                    elif scenario == "shelf_category":
                        context = item.get("shelf_category")

                    label_tasks.append(process_label_item(sem, client, item, model_id, EVAL_MODEL, context))

                label_results = await asyncio.gather(*label_tasks)

                total_aug_score = sum(r[0] for r in label_results)
                total_aug_p_tokens = sum(r[1] for r in label_results)
                total_aug_c_tokens = sum(r[2] for r in label_results)
                label_details = [r[3] for r in label_results]
                avg_aug_score = total_aug_score / len(label_data) if label_data else 0

                # Calculate per-item cost for label augmentation
                avg_aug_input_tokens = (
                    total_aug_p_tokens / len(label_data) if label_data else 0
                )
                avg_aug_output_tokens = (
                    total_aug_c_tokens / len(label_data) if label_data else 0
                )
                avg_aug_cost = ((avg_aug_input_tokens / 1_000_000) * input_price_per_m) + (
                    (avg_aug_output_tokens / 1_000_000) * output_price_per_m
                )

                # --- Product Reranking ---
                print(f"    - Running Product Reranking ({len(rerank_data)} items)...")
                rerank_tasks = []
                for item in rerank_data:
                    context = None
                    if scenario == "product_type":
                        context = item.get("product_type")
                    elif scenario == "shelf_category":
                        context = item.get("shelf_category")
                    rerank_tasks.append(process_rerank_item(sem, client, item, model_id, context))

                rerank_results = await asyncio.gather(*rerank_tasks)

                total_rerank_dist = sum(r[0] for r in rerank_results)
                total_rerank_p_tokens = sum(r[1] for r in rerank_results)
                total_rerank_c_tokens = sum(r[2] for r in rerank_results)
                rerank_details = [r[3] for r in rerank_results]
                avg_rerank_dist = total_rerank_dist / len(rerank_data) if rerank_data else 0

                # Calculate per-item cost for product reranking
                avg_rerank_input_tokens = (
                    total_rerank_p_tokens / len(rerank_data) if rerank_data else 0
                )
                avg_rerank_output_tokens = (
                    total_rerank_c_tokens / len(rerank_data) if rerank_data else 0
                )
                avg_rerank_cost = (
                    (avg_rerank_input_tokens / 1_000_000) * input_price_per_m
                ) + ((avg_rerank_output_tokens / 1_000_000) * output_price_per_m)

                total_input_tokens = total_aug_p_tokens + total_rerank_p_tokens
                total_output_tokens = total_aug_c_tokens + total_rerank_c_tokens

                # Calculate Actual Cost
                # Price is per 1M tokens.
                cost_input = (total_input_tokens / 1_000_000) * input_price_per_m
                cost_output = (total_output_tokens / 1_000_000) * output_price_per_m
                actual_cost = cost_input + cost_output

                end_time = time.time()
                time_taken = end_time - start_time

                results.append(
                    {
                        "model": model_name,
                        "id": model_id,
                        "scenario": scenario,
                        "params": params,
                        "price_input": input_price_per_m,
                        "price_output": output_price_per_m,
                        "aug_score": avg_aug_score,
                        "rerank_dist": avg_rerank_dist,
                        "avg_aug_cost": avg_aug_cost,
                        "avg_rerank_cost": avg_rerank_cost,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                        "actual_cost": actual_cost,
                        "time_taken": time_taken,
                        "note": model_info.get("note", ""),
                        "details": {
                            "label_augmentation": label_details,
                            "product_reranking": rerank_details,
                        },
                    }
                )

                print(
                    f"      > Aug Score: {avg_aug_score:.4f}, Rerank Dist: {avg_rerank_dist:.4f}, Time: {time_taken:.2f}s, Cost: ${actual_cost:.6f}"
                )

        except Exception as e:
            print(f"CRITICAL ERROR benchmarking {model_name}: {e}")
            for scenario in scenarios_to_run:
                results.append(
                    {
                        "model": model_name,
                        "id": model_id,
                        "scenario": scenario,
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
                        "details": {},
                    }
                )
            continue

            # Add or update result in map
            # We treat the new 'results' list as the fresh batch, so we need to merge it back to results_map
            # But wait, 'results' list contains the just-executed stuff.
            pass  # Logic handled below

    # Merge fresh results into the persistent map
    for res in results:
        key = (res["id"], res["scenario"])
        results_map[key] = res

    # Convert map back to list
    final_results = list(results_map.values())

    # Sort results
    final_results.sort(key=lambda x: (x.get("scenario", "base"), x.get("aug_score", 0)), reverse=True)

    # Generate Markdown Report
    markdown_output = "# Benchmark Results\n\n"
    markdown_output += "| Model | Scenario | Params | Total Cost ($) | Label Aug Score | Rerank Dist | Aug Cost/Item ($) | Rerank Cost/Item ($) | Time (s) | Note |\n"
    markdown_output += "|---|---|---|---|---|---|---|---|---|---|\n"

    for res in final_results:
        note = res.get("note", "")
        scen = res.get("scenario", "base")
        markdown_output += f"| {res['model']} | {scen} | {res['params']} | ${res.get('actual_cost', 0):.6f} | {res.get('aug_score', 0):.4f} | {res.get('rerank_dist', 0):.4f} | ${res.get('avg_aug_cost', 0):.6f} | ${res.get('avg_rerank_cost', 0):.6f} | {res.get('time_taken', 0):.2f} | {note} |\n"

    with open("BENCHMARK_RESULTS.md", "w") as f:
        f.write(markdown_output)

    # Save JSON Report
    with open("BENCHMARK_RESULTS.json", "w") as f:
        json.dump(final_results, f, indent=4)

    print(
        "\nBenchmark completed. Results merged and saved to BENCHMARK_RESULTS.md and BENCHMARK_RESULTS.json"
    )


if __name__ == "__main__":
    asyncio.run(run_benchmarks_async())
