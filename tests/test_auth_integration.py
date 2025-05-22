import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import Flask app first
from ui.backend.app import app

class AuthIntegrationTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Setup patches for the specific imported functions
        self.register_patcher = patch('ui.backend.app.register_user')
        self.login_patcher = patch('ui.backend.app.login_user')
        self.verify_patcher = patch('ui.backend.app.verify_token')
        
        self.mock_register = self.register_patcher.start()
        self.mock_login = self.login_patcher.start()
        self.mock_verify = self.verify_patcher.start()
        
        # Configure mock returns with proper dictionaries
        self.mock_register.return_value = {"success": True, "message": "Registration successful", "token": "test_token"}
        self.mock_login.return_value = {
            "success": True,
            "message": "Login successful",
            "token": "test_token",
            "user": {
                "user_id": 1,
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            }
        }
        self.mock_verify.return_value = {
            "success": True,
            "user": {
                "user_id": 1,
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            }
        }
    
    def tearDown(self):
        self.register_patcher.stop()
        self.login_patcher.stop()
        self.verify_patcher.stop()
        
    def _print_test_header(self, test_name):
        print("\n" + "="*60)
        print(f"START TEST: {test_name}")
        print("="*60)

    def _print_test_footer(self, test_name, passed=True):
        status = "PASSED" if passed else "FAILED"
        print("="*60)
        print(f"END TEST: {test_name} - {status}")
        print("="*60 + "\n")

    # --- Registration tests ---

    def test_register_success(self):
        test_name = "Register Success"
        self._print_test_header(test_name)
        payload = {
            'email': 'newuser@example.com',
            'password': 'Password123',
            'user_fname': 'New',
            'user_lname': 'User'
        }
        response = self.client.post('/register', json=payload)
        try:
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertIn('token', data)
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_register_existing_email(self):
        test_name = "Register Existing Email"
        self._print_test_header(test_name)
        # Override for this specific test
        self.mock_register.return_value = {"success": False, "message": "Email already registered"}
        payload = {
            'email': 'existing@example.com',
            'password': 'Password123',
            'user_fname': 'Existing',
            'user_lname': 'User'
        }
        response = self.client.post('/register', json=payload)
        try:
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], "Email already registered")
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_register_missing_fields(self):
        test_name = "Register Missing Fields"
        self._print_test_header(test_name)
        required_fields = ['email', 'password', 'user_fname', 'user_lname']
        try:
            for field in required_fields:
                payload = {
                    'email': 'newuser@example.com',
                    'password': 'Password123',
                    'user_fname': 'New',
                    'user_lname': 'User'
                }
                del payload[field]
                response = self.client.post('/register', json=payload)
                self.assertEqual(response.status_code, 400)
                data = response.get_json()
                self.assertFalse(data['success'])
                self.assertIn('required', data['message'].lower())
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    # --- Login tests ---

    def test_login_success(self):
        test_name = "Login Success"
        self._print_test_header(test_name)
        payload = {
            'email': 'test@example.com',
            'password': 'Password123'
        }
        response = self.client.post('/login', json=payload)
        try:
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertIn('token', data)
            self.assertIn('user', data)
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_login_invalid_email(self):
        test_name = "Login Invalid Email"
        self._print_test_header(test_name)
        # Override for this specific test
        self.mock_login.return_value = {"success": False, "message": "Invalid email or password"}
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'Password123'
        }
        response = self.client.post('/login', json=payload)
        try:
            self.assertEqual(response.status_code, 401)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], "Invalid email or password")
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_login_wrong_password(self):
        test_name = "Login Wrong Password"
        self._print_test_header(test_name)
        # Override for this specific test
        self.mock_login.return_value = {"success": False, "message": "Invalid email or password"}
        payload = {
            'email': 'test@example.com',
            'password': 'wrong_password'
        }
        response = self.client.post('/login', json=payload)
        try:
            self.assertEqual(response.status_code, 401)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], "Invalid email or password")
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_login_missing_fields(self):
        test_name = "Login Missing Fields"
        self._print_test_header(test_name)
        required_fields = ['email', 'password']
        try:
            for field in required_fields:
                payload = {
                    'email': 'test@example.com',
                    'password': 'Password123'
                }
                del payload[field]
                response = self.client.post('/login', json=payload)
                self.assertEqual(response.status_code, 400)
                data = response.get_json()
                self.assertFalse(data['success'])
                self.assertIn('required', data['message'].lower())
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    # --- Token verification tests ---

    def test_verify_token_valid(self):
        test_name = "Verify Token Valid"
        self._print_test_header(test_name)
        payload = {'token': 'valid_token'}
        response = self.client.post('/verify-token', json=payload)
        try:
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertIn('user', data)
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_verify_token_invalid(self):
        test_name = "Verify Token Invalid"
        self._print_test_header(test_name)
        # Override for this specific test
        self.mock_verify.return_value = {"success": False, "message": "Token expired or invalid"}
        payload = {'token': 'invalid_token'}
        response = self.client.post('/verify-token', json=payload)
        try:
            self.assertEqual(response.status_code, 401)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], "Token expired or invalid")
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_verify_token_missing(self):
        test_name = "Verify Token Missing"
        self._print_test_header(test_name)
        response = self.client.post('/verify-token', json={})
        try:
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], "Token is required")
            self._print_test_footer(test_name)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

if __name__ == '__main__':
    unittest.main(verbosity=2)
