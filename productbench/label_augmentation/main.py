import json
import os
import difflib
from openai import OpenAI, OpenAIError

# Initialize OpenAI client
try:
    if os.environ.get("OPENROUTER_KEY"):
        default_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_KEY")
        )
    else:
        default_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except OpenAIError:
    default_client = None

def load_data(file_path):
  """Loads the label augmentation data from a JSON file."""
  with open(file_path, 'r') as f:
    return json.load(f)

def augment_label(label: str, model: str = "google/gemini-3-flash-preview", client: OpenAI = None) -> str:
  """Uses an LLM to augment the product label."""
  use_client = client if client else default_client

  if not use_client or not use_client.api_key:
      # Fallback if API key is not available
      return f"Augmented: {label} (No API Key)"

  try:
    response = use_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that improves product labels. Your goal is to make the label more descriptive and human-readable, expanding abbreviations and adding missing context if possible."},
            {"role": "user", "content": f"Augment this product label: '{label}'"}
        ],
        temperature=0.3,
        max_tokens=60
    )
    return response.choices[0].message.content.strip()
  except Exception as e:
      print(f"Error calling OpenAI API: {e}")
      return f"Augmented: {label} (Error)"

def evaluate_augmentation(augmented_label: str, ground_truth: str, model: str = "google/gemini-3-flash-preview", client: OpenAI = None) -> float:
  """
  Evaluates the quality of the augmented label against the ground truth using an LLM.
  Returns a score between 0.0 and 1.0.
  Falls back to a token overlap metric if the OpenAI API key is missing or an error occurs.
  """
  use_client = client if client else default_client

  if use_client and use_client.api_key:
    try:
      prompt = (
          f"Compare the augmented label with the ground truth label.\n"
          f"Augmented Label: {augmented_label}\n"
          f"Ground Truth: {ground_truth}\n"
          f"Rate the semantic similarity and correctness on a scale from 0.0 to 1.0, "
          f"where 1.0 means they are identical in meaning and 0.0 means they are completely unrelated.\n"
          f"Return ONLY the numeric score."
      )

      response = use_client.chat.completions.create(
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
        # If LLM returns non-numeric, fallback or log error.
        pass

    except Exception as e:
      # Log the error if needed, but for now we proceed to fallback
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
