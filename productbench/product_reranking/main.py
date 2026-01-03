import json
import math

def load_data(file_path):
  """Loads the product re-ranking data from a JSON file."""
  with open(file_path, 'r') as f:
    return json.load(f)

def rerank_products(query: str, products: list) -> list:
  """Placeholder function to simulate LLM product re-ranking."""
  return [0, 1]

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
