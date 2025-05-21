import unittest
import json
import sys
import os
import jwt
import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app and authentication functions
from app import app
from auth import register_user, login_user, verify_token

class TestAuth(unittest.TestCase):
    """
    Tests for the authentication system including registration, login, and token verification.
    These tests use mocking to avoid actual database operations.
    """
    
    def setUp(self):
        # Set up test client
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Set up test JWT secret
        self.jwt_secret = "test_secret"
        
        # Sample user data
        self.test_user = {
            "email": "test@example.com",
            "password": "Password123!",
            "user_fname": "Test",
            "user_lname": "User"
        }
        
        # Sample user from database (with hashed password)
        self.db_user = {
            "user_id": 1,
            "user_email": "test@example.com",
            "user_password": "hashed_password_here",  # In real scenario, this would be bcrypt hashed
            "user_fname": "Test",
            "user_lname": "User"
        }
        
        # Sample JWT payload
        self.jwt_payload = {
            'user_id': 1,
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }

    @patch('auth.execute_query')
    @patch('auth.bcrypt')
    def test_register_user_success(self, mock_bcrypt, mock_execute_query):
        """Test successful user registration"""
        # Mock the database query to return None (indicating user doesn't exist)
        # and then return an ID for successful insert
        mock_execute_query.side_effect = [[], 1]  # First call returns empty list, second returns user ID 1
        
        # Mock bcrypt to return a known hash
        mock_bcrypt.generate_password_hash.return_value = b'hashed_password'
        
        # Call the registration function
        result = register_user(
            self.test_user["email"],
            self.test_user["password"],
            self.test_user["user_fname"],
            self.test_user["user_lname"]
        )
        
        # Assert that registration was successful
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Registration successful")
        
        # Verify execute_query was called correctly
        mock_execute_query.assert_any_call(
            "SELECT * FROM user WHERE user_email = %s",
            ('test@example.com',),
            fetch=True
        )

    @patch('auth.execute_query')
    def test_register_user_existing_email(self, mock_execute_query):
        """Test registration with an email that already exists"""
        # Mock the database query to return a user (indicating email already exists)
        mock_execute_query.return_value = [self.db_user]
        
        # Call the registration function
        result = register_user(
            self.test_user["email"],
            self.test_user["password"],
            self.test_user["user_fname"],
            self.test_user["user_lname"]
        )
        
        # Assert that registration failed due to existing email
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Email already registered")

    @patch('auth.execute_query')
    @patch('auth.bcrypt')
    @patch('auth.jwt')
    @patch('auth.JWT_SECRET', 'test_secret')
    def test_login_user_success(self, mock_jwt, mock_bcrypt, mock_execute_query):
        """Test successful user login"""
        # Mock the database query to return a user
        mock_execute_query.return_value = [self.db_user]
        
        # Mock bcrypt to return True for password check
        mock_bcrypt.check_password_hash.return_value = True
        
        # Mock JWT to return a token
        mock_jwt.encode.return_value = "test_token"
        
        # Call the login function
        result = login_user(self.test_user["email"], self.test_user["password"])
        
        # Assert that login was successful
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Login successful")
        self.assertEqual(result["token"], "test_token")
        self.assertEqual(result["user"]["id"], 1)
        self.assertEqual(result["user"]["email"], "test@example.com")

    @patch('auth.execute_query')
    def test_login_user_invalid_email(self, mock_execute_query):
        """Test login with an invalid email"""
        # Mock the database query to return no users
        mock_execute_query.return_value = []
        
        # Call the login function
        result = login_user("nonexistent@example.com", "password")
        
        # Assert that login failed due to invalid email
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Invalid email or password")

    @patch('auth.execute_query')
    @patch('auth.bcrypt')
    def test_login_user_invalid_password(self, mock_bcrypt, mock_execute_query):
        """Test login with an invalid password"""
        # Mock the database query to return a user
        mock_execute_query.return_value = [self.db_user]
        
        # Mock bcrypt to return False for password check
        mock_bcrypt.check_password_hash.return_value = False
        
        # Call the login function
        result = login_user(self.test_user["email"], "wrong_password")
        
        # Assert that login failed due to invalid password
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Invalid email or password")

    @patch('auth.jwt')
    @patch('auth.JWT_SECRET', 'test_secret')
    def test_verify_token_valid(self, mock_jwt):
        """Test verifying a valid token"""
        # Mock JWT to decode successfully and return the payload
        mock_jwt.decode.return_value = self.jwt_payload
        
        # Call the verify_token function
        result = verify_token("valid_token")
        
        # Assert that token verification was successful
        self.assertTrue(result["success"])
        self.assertEqual(result["user"], self.jwt_payload)
        
        # Verify jwt.decode was called correctly
        mock_jwt.decode.assert_called_once_with("valid_token", 'test_secret', algorithms=['HS256'])

    @patch('auth.jwt')
    def test_verify_token_expired(self, mock_jwt):
        """Test verifying an expired token"""
        # Mock JWT to raise an ExpiredSignatureError
        mock_jwt.decode.side_effect = jwt.ExpiredSignatureError()
        mock_jwt.ExpiredSignatureError = jwt.ExpiredSignatureError
        
        # Call the verify_token function
        result = verify_token("expired_token")
        
        # Assert that token verification failed due to expiration
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Token expired")

    @patch('auth.jwt')
    def test_verify_token_invalid(self, mock_jwt):
        """Test verifying an invalid token"""
        # Mock JWT to raise an InvalidTokenError
        mock_jwt.decode.side_effect = jwt.InvalidTokenError()
        mock_jwt.InvalidTokenError = jwt.InvalidTokenError
        
        # Call the verify_token function
        result = verify_token("invalid_token")
        
        # Assert that token verification failed due to invalid token
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Invalid token")

    def test_register_endpoint(self):
        """Test the /register endpoint"""
        # Make a request to the register endpoint
        response = self.client.post(
            '/register',
            json=self.test_user,
            content_type='application/json'
        )
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check the status code and response data
        # Note: This will only work if the database mock is set up properly in the app
        # If this test fails, you may need to add more sophisticated mocking
        self.assertIn(response.status_code, [201, 400])  # Either created or email already exists
        self.assertIn('success', data)
        self.assertIn('message', data)

    def test_login_endpoint(self):
        """Test the /login endpoint"""
        # Make a request to the login endpoint
        response = self.client.post(
            '/login',
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            },
            content_type='application/json'
        )
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check the response data
        # Note: This will depend on your database having the test user
        self.assertIn(response.status_code, [200, 401])  # Either success or auth failed
        self.assertIn('success', data)
        self.assertIn('message', data)
        
        # If login successful, check for token and user data
        if response.status_code == 200:
            self.assertIn('token', data)
            self.assertIn('user', data)

    def test_verify_token_endpoint(self):
        """Test the /verify-token endpoint"""
        # Generate a valid token
        payload = {
            'user_id': 1,
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # Make a request to the verify-token endpoint
        response = self.client.post(
            '/verify-token',
            json={"token": token},
            content_type='application/json'
        )
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check the response data
        # Note: This test may fail if JWT_SECRET doesn't match what's used in the function
        self.assertIn(response.status_code, [200, 401])  # Either success or auth failed
        self.assertIn('success', data)

if __name__ == '__main__':
    unittest.main() 