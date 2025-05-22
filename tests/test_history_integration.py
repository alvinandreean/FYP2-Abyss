import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock dependencies before importing app
import sys
sys.modules['fgsm'] = MagicMock()
sys.modules['db'] = MagicMock()
sys.modules['jwt'] = MagicMock()
sys.modules['flask_bcrypt'] = MagicMock()
sys.modules['auth'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv'].load_dotenv = MagicMock()

from ui.backend.app import app

class HistoryEndpointTest(unittest.TestCase):

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

    @patch('ui.backend.app.verify_token')
    @patch('ui.backend.app.execute_query')
    def test_history_success_with_data(self, mock_execute_query, mock_verify_token):
        test_name = "History Retrieval Success With Data"
        self._print_test_header(test_name)

        # Mock valid token
        mock_verify_token.return_value = {"success": True, "user": {"user_id": 1}}

        # Mock DB returns some attack history
        mock_execute_query.return_value = [
            {
                "id": 1,
                "user_id": 1,
                "model_used": "mobilenet_v2",
                "epsilon_used": 0.05,
                "orig_class": "cat",
                "orig_conf": 0.95,
                "adv_class": "dog",
                "adv_conf": 0.7,
                "created_at": "2025-01-01 12:00:00"
            }
        ]

        try:
            headers = {"Authorization": "Bearer valid_token"}
            response = self.client.get('/history', headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertIsInstance(data['history'], list)
            self.assertGreater(len(data['history']), 0)
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    @patch('ui.backend.app.verify_token')
    @patch('ui.backend.app.execute_query')
    def test_history_success_empty(self, mock_execute_query, mock_verify_token):
        test_name = "History Retrieval Success Empty"
        self._print_test_header(test_name)

        # Mock valid token
        mock_verify_token.return_value = {"success": True, "user": {"user_id": 1}}

        # Mock DB returns empty list (no history)
        mock_execute_query.return_value = []

        try:
            headers = {"Authorization": "Bearer valid_token"}
            response = self.client.get('/history', headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertIsInstance(data['history'], list)
            self.assertEqual(len(data['history']), 0)
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    @patch('ui.backend.app.verify_token')
    def test_history_unauthorized_invalid_token(self, mock_verify_token):
        test_name = "History Unauthorized Invalid Token"
        self._print_test_header(test_name)

        # Mock invalid token verification
        mock_verify_token.return_value = {"success": False, "message": "Token expired or invalid"}

        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = self.client.get('/history', headers=headers)
            self.assertEqual(response.status_code, 401)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Unauthorized')
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

if __name__ == '__main__':
    unittest.main(verbosity=2)
