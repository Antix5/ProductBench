# ProductBench: LLM Benchmark for Product Knowledge

ProductBench is a benchmark designed to evaluate the product knowledge of Large Language Models (LLMs). It consists of two main tasks:

*   **Label Augmentation:** The LLM is given a condensed or ambiguous product label and must output a clear, human-readable label.
*   **Product Re-ranking:** The LLM is given a search query and a list of potential product matches, and it must re-rank the products from most to least relevant.

The project also includes a web-based UI with a leaderboard to visualize the results and a price-to-performance graph.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/productbench.git
    cd productbench
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the benchmarks and launch the web UI, execute the `main.py` script:

```bash
python main.py
```

The application will be available at `http://127.0.0.1:5001`.

## Project Structure

*   `main.py`: The main entry point for running the benchmarks and launching the UI.
*   `requirements.txt`: The list of Python dependencies.
*   `productbench/`: The main project directory.
    *   `data/`: Contains the JSON data for the benchmarks.
    *   `label_augmentation/`: The logic for the label augmentation task.
    *   `product_reranking/`: The logic for the product re-ranking task.
    *   `ui/`: The Flask web application for the leaderboard.
        *   `app.py`: The Flask application factory.
        *   `static/`: CSS and JavaScript files.
        *   `templates/`: HTML templates.
