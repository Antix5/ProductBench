import json
import os
import difflib
from openai import OpenAI, OpenAIError

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except OpenAIError:
    client = None

def load_data(file_path):
  """Loads the label augmentation data from a JSON file."""
  with open(file_path, 'r') as f:
    return json.load(f)

def augment_label(label: str) -> str:
  """Uses an LLM to augment the product label."""
  if not client or not client.api_key:
      # Fallback if API key is not available
      return f"Augmented: {label} (No API Key)"

  try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
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

def evaluate_augmentation(augmented_label: str, ground_truth: str) -> float:
  """Calculates the similarity between the augmented label and the ground truth."""
  matcher = difflib.SequenceMatcher(None, augmented_label.lower(), ground_truth.lower())
  return matcher.ratio()
