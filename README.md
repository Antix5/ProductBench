# ProductBench: LLM Benchmark for Product Knowledge

ProductBench is a benchmark designed to evaluate the product knowledge of Large
Language Models (LLMs). It consists of two main tasks:

- **Label Augmentation:** The LLM is given a condensed or ambiguous product
  label and must output a clear, human-readable label.
- **Product Re-ranking:** The LLM is given a search query and a list of
  potential product matches, and it must re-rank the products from most to least
  relevant.

The project also includes a web-based UI with a leaderboard to visualize the
results and a price-to-performance graph.

## Methodology

The goal of this benchmark is to estimate which model would be the most relevant
for a product RAG system like a recommendation system, and measure both domain
specific language as well as the ability to understand noisy labels (corrupted
text, with brands...).

The models currently evaluated are mostly non-thinking ones because they are the
one where the latency is the smallest.

Qwen 3 model have been tested in a previous iterations of the benchmark but has
a weird behaviour (unreliable to benchmark), they have therefore been discarded
for the time being and will certainly be reintroduced when the quirks have been
solved (like the need of the /nothink mention).

The exception to the non thinking model category is gemini flash 3 which is the
judge model (clearly specified in the leaderboard).

This benchmark is fully reproducible suign the "benchmark runner" script.

## Limitation
This benchmark being open source on github, it it possible that that the benchmark will be
added in future LLM training datasets, which they could overfit onto. Model released before the 4th of January 2026
should be contamination free.

Gemini 3 Pro has been used to get inspirations for some of the examples, especially in languages like German, Spanish and Polish. All examples of the benchmark have been human picked or adjusted.
The UI and the benchmark logic have been in part vibe coded.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/productbench.git
   cd productbench
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the benchmarks, execute the `benchmark_runner.py` script:

```bash
python benchmark_runner.py
```

The website is a static one, so just go on index.html to see the leaderboard at the end

## Project Structure

- `main.py`: The main entry point for running the benchmarks and launching the
  UI.
- `requirements.txt`: The list of Python dependencies.
- `productbench/`: The main project directory.
  - `data/`: Contains the JSON data for the benchmarks.
  - `label_augmentation/`: The logic for the label augmentation task.
  - `product_reranking/`: The logic for the product re-ranking task.
  - `ui/`: The Flask web application for the leaderboard.
    - `app.py`: The Flask application factory.
    - `static/`: CSS and JavaScript files.
    - `templates/`: HTML templates.
