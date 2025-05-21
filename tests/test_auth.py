import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock the db module before importing auth
sys.modules['db'] = MagicMock()

# Mock dotenv
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv'].load_dotenv = MagicMock()

# Import the authentication functions - using patch for JWT_SECRET
with patch.dict('os.environ', {'JWT_SECRET': 'test_secret'}):
    from ui.backend.auth import register_user, login_user, verify_token

class AuthTest(unittest.TestCase):
    """
    Authentication tests for core functions
    """
    
    def setUp(self):
        # Set up environment variables patch
        self.env_patcher = patch.dict('os.environ', {'JWT_SECRET': 'test_secret'})
        self.env_patcher.start()
        
        # Sample user data
        self.email = "test@example.com"
        self.password = "Password123"
        self.first_name = "Test"
        self.last_name = "User"
        
        # Sample database user
        self.db_user = {
            'user_id': 1,
            'user_email': self.email,
            'user_password': 'hashed_password',
            'user_fname': self.first_name,
            'user_lname': self.last_name
        }

    def tearDown(self):
        # Stop the environment patcher
        self.env_patcher.stop()

    @patch('ui.backend.auth.execute_query')
    @patch('ui.backend.auth.bcrypt')
    def test_register_user_success(self, mock_bcrypt, mock_execute_query):
        """Test successful user registration"""
        # Mock the database queries
        mock_execute_query.side_effect = [[], 1]  # First returns [] (user not found), then returns 1 (user_id)
        
        # Mock password hashing
        mock_bcrypt.generate_password_hash.return_value = b'hashed_password'
        
        # Call the function
        result = register_user(self.email, self.password, self.first_name, self.last_name)
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], "Registration successful")

    @patch('ui.backend.auth.execute_query')
    def test_register_user_existing_email(self, mock_execute_query):
        """Test registration with an existing email"""
        # Mock the database query to return a user (email exists)
        mock_execute_query.return_value = [self.db_user]
        
        # Call the function
        result = register_user(self.email, self.password, self.first_name, self.last_name)
        
        # Check result
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Email already registered")

    @patch('ui.backend.auth.execute_query')
    @patch('ui.backend.auth.bcrypt')
    @patch('ui.backend.auth.jwt')
    def test_login_user_success(self, mock_jwt, mock_bcrypt, mock_execute_query):
        """Test successful login"""
        # Mock the database query
        mock_execute_query.return_value = [self.db_user]
        
        # Mock password verification
        mock_bcrypt.check_password_hash.return_value = True
        
        # Mock JWT token generation
        mock_jwt.encode.return_value = "test_token"
        
        # Call the function
        result = login_user(self.email, self.password)
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], "Login successful")
        self.assertEqual(result['token'], "test_token")
        self.assertEqual(result['user']['email'], self.email)

    @patch('ui.backend.auth.execute_query')
    def test_login_user_invalid_email(self, mock_execute_query):
        """Test login with invalid email"""
        # Mock the database query to return no users
        mock_execute_query.return_value = []
        
        # Call the function
        result = login_user("wrong@example.com", self.password)
        
        # Check result
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Invalid email or password")

    @patch('ui.backend.auth.jwt')
    def test_verify_token_valid(self, mock_jwt):
        """Test verifying a valid token"""
        # Create a mock payload
        mock_payload = {
            'user_id': 1,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
        
        # Mock JWT decode
        mock_jwt.decode.return_value = mock_payload
        
        # Call the function
        result = verify_token("valid_token")
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['user'], mock_payload)

    @patch('ui.backend.auth.jwt')
    def test_verify_token_expired(self, mock_jwt):
        """Test verifying an expired token"""
        # Import the actual JWT exceptions
        import jwt as real_jwt
        
        # Mock JWT to raise an ExpiredSignatureError
        mock_jwt.decode.side_effect = real_jwt.ExpiredSignatureError()
        mock_jwt.ExpiredSignatureError = real_jwt.ExpiredSignatureError
        
        # Call the function
        result = verify_token("expired_token")
        
        # Check result
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], "Token expired")

if __name__ == '__main__':
    unittest.main() 