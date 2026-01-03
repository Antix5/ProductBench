import unittest
from unittest.mock import MagicMock, patch
import os
import json
from productbench.product_reranking.main import rerank_products

class TestRerankProducts(unittest.TestCase):

    @patch("productbench.product_reranking.main.OpenAI")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
    def test_rerank_products_success(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "[1, 0, 3, 2]"

        mock_client.chat.completions.create.return_value = mock_response

        products = ["Product A", "Product B", "Product C", "Product D"]
        query = "test query"

        result = rerank_products(query, products)

        self.assertEqual(result, [1, 0, 3, 2])
        mock_client.chat.completions.create.assert_called_once()

    @patch("productbench.product_reranking.main.OpenAI")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
    def test_rerank_products_invalid_json(self, mock_openai):
        # Setup mock to return invalid JSON
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not a JSON list"

        mock_client.chat.completions.create.return_value = mock_response

        products = ["Product A", "Product B"]
        query = "test query"

        # Should return default order [0, 1]
        result = rerank_products(query, products)

        self.assertEqual(result, [0, 1])

    @patch("productbench.product_reranking.main.OpenAI")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
    def test_rerank_products_api_error(self, mock_openai):
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        products = ["Product A", "Product B"]
        query = "test query"

        result = rerank_products(query, products)

        self.assertEqual(result, [0, 1])

    @patch.dict(os.environ, {}, clear=True)
    def test_rerank_products_no_api_key(self):
        # Ensure no API key is set
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        products = ["Product A", "Product B"]
        query = "test query"

        result = rerank_products(query, products)

        self.assertEqual(result, [0, 1])

if __name__ == "__main__":
    unittest.main()
