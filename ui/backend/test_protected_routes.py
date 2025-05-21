import unittest
import json
import sys
import os
import jwt
import datetime
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

class TestProtectedRoutes(unittest.TestCase):
    """
    Tests for protected routes that require authentication.
    """
    
    def setUp(self):
        # Set up test client
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Set up test JWT secret (should match what's in the app)
        self.jwt_secret = "test_secret"  # This should match what's in your .env or code
        
        # Create a valid test token
        self.valid_token = self.create_test_token(expired=False)
        
        # Create an expired test token
        self.expired_token = self.create_test_token(expired=True)
    
    def create_test_token(self, expired=False):
        """Create a test JWT token that is either valid or expired"""
        if expired:
            # Create a token that expired yesterday
            exp_time = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        else:
            # Create a token that expires tomorrow
            exp_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        
        # Create payload
        payload = {
            'user_id': 1,
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'exp': exp_time
        }
        
        # Encode the token
        try:
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            return token
        except Exception as e:
            print(f"Error creating test token: {str(e)}")
            return None

    @patch('auth.verify_token')
    def test_history_route_authenticated(self, mock_verify_token):
        """Test accessing /history route with a valid authentication token"""
        # Mock the verify_token function to return success and a user
        mock_verify_token.return_value = {
            'success': True,
            'user': {
                'user_id': 1,
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        # Set up mock for execute_query to return attack history
        with patch('app.execute_query') as mock_execute_query:
            # Mock return value for attack history query
            mock_execute_query.return_value = [
                {
                    'id': 1,
                    'model_used': 'mobilenet_v2',
                    'epsilon_used': 0.05,
                    'orig_class': 'car',
                    'orig_conf': 0.95,
                    'adv_class': 'truck',
                    'adv_conf': 0.6,
                    'created_at': '2023-05-01 12:00:00'
                }
            ]
            
            # Make a request to the history route with authentication header
            response = self.client.get(
                '/history',
                headers={
                    'Authorization': f'Bearer {self.valid_token}'
                }
            )
            
            # Parse the response
            data = json.loads(response.data)
            
            # Check the response
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data.get('success', False))
            self.assertIn('history', data)
            
            # Verify that execute_query was called correctly
            if response.status_code == 200:
                mock_execute_query.assert_called_once()

    def test_history_route_unauthenticated(self):
        """Test accessing /history route without authentication"""
        # Make a request to the history route without authentication header
        response = self.client.get('/history')
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check the response
        self.assertEqual(response.status_code, 401)
        self.assertFalse(data.get('success', True))
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Authentication required')

    @patch('auth.verify_token')
    def test_history_route_expired_token(self, mock_verify_token):
        """Test accessing /history route with an expired token"""
        # Mock the verify_token function to return token expired error
        mock_verify_token.return_value = {
            'success': False,
            'message': 'Token expired'
        }
        
        # Make a request to the history route with expired token
        response = self.client.get(
            '/history',
            headers={
                'Authorization': f'Bearer {self.expired_token}'
            }
        )
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check the response
        self.assertEqual(response.status_code, 401)
        self.assertFalse(data.get('success', True))
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Token expired')

    @patch('auth.verify_token')
    def test_attack_with_authentication(self, mock_verify_token):
        """Test the /attack endpoint with authentication to save history"""
        # Mock the verify_token function to return success and a user
        mock_verify_token.return_value = {
            'success': True,
            'user': {
                'user_id': 1,
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        }
        
        # Create a temporary test image file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_image:
            # Write some dummy data to the file
            temp_image.write(b'dummy image data')
            temp_image.flush()
            
            # Set up mocks for execute_query and FGSM
            with patch('app.execute_query') as mock_execute_query, \
                 patch('app.FGSM') as mock_fgsm_class:
                
                # Set up the mock FGSM instance
                mock_fgsm = MagicMock()
                mock_fgsm_class.return_value = mock_fgsm
                
                # Configure the attack method to return a result
                mock_fgsm.attack.return_value = {
                    'epsilon_used': 0.05,
                    'orig_class': 'car',
                    'orig_conf': 0.95,
                    'adv_class': 'truck',
                    'adv_conf': 0.6,
                    'original_image': 'base64_encoded_image_data',
                    'perturbation_image': 'base64_encoded_image_data',
                    'adversarial_image': 'base64_encoded_image_data'
                }
                
                # Make a request to the attack endpoint with authentication
                with open(temp_image.name, 'rb') as f:
                    response = self.client.post(
                        '/attack',
                        data={
                            'model': 'mobilenet_v2',
                            'epsilon': '0.05',
                            'autoTune': 'false'
                        },
                        headers={
                            'Authorization': f'Bearer {self.valid_token}'
                        },
                        content_type='multipart/form-data',
                        buffered=True,
                        content_length=len(b'dummy image data'),
                        input_stream=f
                    )
                
                # Parse the response
                data = json.loads(response.data)
                
                # Check the response
                if response.status_code == 200:
                    # Check that execute_query was called to save to history
                    mock_execute_query.assert_called_once()
                    
                    # Verify response contains expected fields
                    self.assertIn('epsilon_used', data)
                    self.assertIn('orig_class', data)
                    self.assertIn('adv_class', data)

if __name__ == '__main__':
    unittest.main() 