import unittest
from unittest.mock import patch, MagicMock
from productbench.label_augmentation.main import augment_label, evaluate_augmentation

class TestLabelAugmentation(unittest.TestCase):

    @patch('productbench.label_augmentation.main.default_client')
    def test_augment_label_success(self, mock_client):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Augmented Label"
        mock_client.chat.completions.create.return_value = mock_response
        mock_client.api_key = "dummy_key"

        # Call without explicit client, so it uses default_client
        result = augment_label("Original Label")
        self.assertEqual(result, "Augmented Label")
        mock_client.chat.completions.create.assert_called_once()

    @patch('productbench.label_augmentation.main.default_client')
    def test_augment_label_no_api_key(self, mock_client):
        # Simulate no API key
        mock_client.api_key = None

        result = augment_label("Original Label")
        self.assertIn("No API Key", result)

    def test_evaluate_augmentation(self):
        score = evaluate_augmentation("apple", "apple")
        self.assertEqual(score, 1.0)

        score = evaluate_augmentation("apple", "banana")
        self.assertLess(score, 0.5)

        score = evaluate_augmentation("Apple iPhone", "apple iphone")
        self.assertEqual(score, 1.0)

if __name__ == '__main__':
    unittest.main()
