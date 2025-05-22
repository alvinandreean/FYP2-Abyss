import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock modules before importing app
sys.modules['fgsm'] = MagicMock()
sys.modules['db'] = MagicMock()
sys.modules['jwt'] = MagicMock()
sys.modules['flask_bcrypt'] = MagicMock()
sys.modules['auth'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv'].load_dotenv = MagicMock()

from ui.backend.app import app

class AvailableImagesTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def _print_test_header(self, test_name):
        print("\n" + "="*50)
        print(f"START TEST: {test_name}")
        print("="*50)

    def _print_test_footer(self, test_name, passed=True):
        status = "PASSED" if passed else "FAILED"
        print("="*50)
        print(f"END TEST: {test_name} - {status}")
        print("="*50 + "\n")

    @patch('ui.backend.app.execute_query')
    def test_get_images_success_non_empty(self, mock_execute_query):
        test_name = "Get Images Success Non-Empty"
        self._print_test_header(test_name)

        mock_execute_query.return_value = [
            {'image_filename': 'cat.jpg', 'image_label': 'cat', 'image_url': 'http://example.com/cat.jpg'},
            {'image_filename': 'dog.jpg', 'image_label': 'dog', 'image_url': 'http://example.com/dog.jpg'}
        ]

        try:
            response = self.client.get('/available-images')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(len(data['images']), 2)
            self.assertEqual(data['images'][0]['filename'], 'cat.jpg')
            self.assertEqual(data['images'][1]['label'], 'dog')
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    @patch('ui.backend.app.execute_query')
    def test_get_images_success_empty(self, mock_execute_query):
        test_name = "Get Images Success Empty"
        self._print_test_header(test_name)

        mock_execute_query.return_value = []

        try:
            response = self.client.get('/available-images')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(len(data['images']), 0)
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    @patch('ui.backend.app.execute_query')
    def test_get_images_db_failure(self, mock_execute_query):
        test_name = "Get Images Database Failure"
        self._print_test_header(test_name)

        mock_execute_query.side_effect = Exception("Database failure")

        try:
            response = self.client.get('/available-images')
            self.assertEqual(response.status_code, 500)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertIn('Error fetching images', data['message'])
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

if __name__ == '__main__':
    unittest.main(verbosity=2)
