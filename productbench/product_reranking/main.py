import json
import math
import os
from openai import OpenAI

def load_data(file_path):
  """Loads the product re-ranking data from a JSON file."""
  with open(file_path, 'r') as f:
    return json.load(f)

def rerank_products(query: str, products: list) -> list:
  """
  Reranks products using an LLM.

  Args:
      query: The user query.
      products: A list of product strings.

  Returns:
      A list of indices representing the reranked order of products.
  """
  api_key = os.environ.get("OPENAI_API_KEY")

  if not api_key:
      # Fallback if no API key is provided
      print("Warning: OPENAI_API_KEY not found. Returning original order.")
      return list(range(len(products)))

  client = OpenAI(api_key=api_key)

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
      response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
              {"role": "system", "content": "You are a helpful assistant that ranks products."},
              {"role": "user", "content": prompt}
          ],
          temperature=0
      )

      content = response.choices[0].message.content.strip()
      # Try to extract JSON list if there's extra text
      if "[" in content and "]" in content:
          start = content.find("[")
          end = content.rfind("]") + 1
          content = content[start:end]

      ranked_indices = json.loads(content)

      # Validate indices
      if isinstance(ranked_indices, list) and all(isinstance(i, int) for i in ranked_indices):
          # Ensure all original indices are present (optional, but good for reranking)
          # Or just return what the LLM gave, trusting it.
          # But for safety, let's filter valid indices.
          valid_indices = [i for i in ranked_indices if 0 <= i < len(products)]

          # Add missing indices at the end
          existing_set = set(valid_indices)
          for i in range(len(products)):
              if i not in existing_set:
                  valid_indices.append(i)

          return valid_indices
      else:
           print(f"Error: LLM returned invalid format: {content}")
           return list(range(len(products)))

  except Exception as e:
      print(f"Error calling OpenAI API: {e}")
      return list(range(len(products)))

def dcg(relevance_scores):
    """Discounted Cumulative Gain."""
    return sum((score / math.log2(i + 2)) for i, score in enumerate(relevance_scores))

def ndcg(predicted_ranking, ground_truth_ranking):
    """Normalized Discounted Cumulative Gain."""
    relevance_scores = [1 if item in ground_truth_ranking else 0 for item in predicted_ranking]

    ideal_relevance_scores = [1] * len(ground_truth_ranking)

    actual_dcg = dcg(relevance_scores)
    ideal_dcg = dcg(ideal_relevance_scores)

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg

def calculate_ranking_distance(predicted_ranking: list, ground_truth_ranking: list) -> float:
  """Calculates the ranking distance between the predicted and ground truth rankings."""
  return 1 - ndcg(predicted_ranking, ground_truth_ranking)
