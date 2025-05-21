import unittest
import sys
import os
import io
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock the required modules
sys.modules['tensorflow'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()

# Create mock for FGSM
mock_fgsm_instance = MagicMock()
mock_fgsm_class = MagicMock()
mock_fgsm_class.return_value = mock_fgsm_instance

# Mock the FGSM module
sys.modules['fgsm'] = MagicMock()
sys.modules['fgsm.fgsm'] = MagicMock()
sys.modules['fgsm.fgsm'].FGSM = mock_fgsm_class

# Mock database module
sys.modules['db'] = MagicMock()
sys.modules['db'].execute_query = MagicMock()

# Mock jwt and bcrypt
sys.modules['jwt'] = MagicMock()
sys.modules['flask_bcrypt'] = MagicMock()

# Mock dotenv
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv'].load_dotenv = MagicMock()

# Now import the Flask app
with patch.dict('os.environ', {'JWT_SECRET': 'test_secret'}):
    from ui.backend.app import app

class ImageUploadTest(unittest.TestCase):
    """
    Tests for the image upload functionality in the attack endpoint
    """
    
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Create a mock image file
        self.mock_image_data = b'mock image data'
        
        # Create a mock response for FGSM attack
        self.mock_attack_result = {
            'epsilon_used': 0.05,
            'orig_class': 'cat',
            'orig_conf': 0.95,
            'adv_class': 'dog',
            'adv_conf': 0.7,
            'original_image': 'base64_encoded_image_data',
            'perturbation_image': 'base64_encoded_image_data',
            'adversarial_image': 'base64_encoded_image_data'
        }
        
        # Configure the mock FGSM instance
        mock_fgsm_instance.attack.return_value = self.mock_attack_result
        
        # Set up filesystem mock
        self.file_mock_patcher = patch('builtins.open', create=True)
        self.mock_file = self.file_mock_patcher.start()
        
        # Set up os.remove mock to avoid file deletion errors
        self.remove_patcher = patch('os.remove')
        self.mock_remove = self.remove_patcher.start()
        
    def tearDown(self):
        self.file_mock_patcher.stop()
        self.remove_patcher.stop()
        
    def test_attack_with_valid_image_upload(self):
        """Test uploading an image for FGSM attack"""
        # Create test data
        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',
            'autoTune': 'false'
        }
        
        # Create a file object
        file_data = io.BytesIO(self.mock_image_data)
        
        # Make the request
        response = self.client.post(
            '/attack',
            data=data,
            content_type='multipart/form-data',
            buffered=True,
            content_length=len(self.mock_image_data),
            data={'image': (file_data, 'test_image.jpg')}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Parse the response JSON
        response_data = json.loads(response.data)
        
        # Verify it contains the expected fields
        self.assertEqual(response_data['orig_class'], 'cat')
        self.assertEqual(response_data['adv_class'], 'dog')
        self.assertEqual(response_data['model_used'], 'mobilenet_v2')
        
    def test_attack_missing_image(self):
        """Test attack without providing an image"""
        # Create test data without an image
        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',
            'autoTune': 'false'
        }
        
        # Make the request
        response = self.client.post(
            '/attack',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        
        # Parse the response JSON
        response_data = json.loads(response.data)
        
        # Verify it contains the expected error message
        self.assertEqual(response_data['error'], 'No image or model provided')
        
    def test_attack_missing_model(self):
        """Test attack without specifying a model"""
        # Create test data without model
        data = {
            'epsilon': '0.05',
            'autoTune': 'false'
        }
        
        # Create a file object
        file_data = io.BytesIO(self.mock_image_data)
        
        # Make the request
        response = self.client.post(
            '/attack',
            data=data,
            content_type='multipart/form-data',
            buffered=True,
            content_length=len(self.mock_image_data),
            data={'image': (file_data, 'test_image.jpg')}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        
        # Parse the response JSON
        response_data = json.loads(response.data)
        
        # Verify it contains the expected error message
        self.assertEqual(response_data['error'], 'No image or model provided')
        
    def test_attack_with_auto_tune(self):
        """Test attack with auto-tuning enabled"""
        # Configure the mock FGSM instance for auto-tuning
        mock_fgsm_instance.auto_tune_attack.return_value = self.mock_attack_result
        
        # Create test data with auto-tuning enabled
        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',
            'autoTune': 'true'
        }
        
        # Create a file object
        file_data = io.BytesIO(self.mock_image_data)
        
        # Make the request
        response = self.client.post(
            '/attack',
            data=data,
            content_type='multipart/form-data',
            buffered=True,
            content_length=len(self.mock_image_data),
            data={'image': (file_data, 'test_image.jpg')}
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Verify auto_tune_attack was called instead of attack
        mock_fgsm_instance.auto_tune_attack.assert_called_once()
        mock_fgsm_instance.attack.assert_not_called()

if __name__ == '__main__':
    unittest.main() 