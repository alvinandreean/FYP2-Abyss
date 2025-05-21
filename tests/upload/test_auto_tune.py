import unittest
import sys
import os
import io
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import the mock setup helper
from tests.upload.mock_setup import setup_mocks

# Setup all mocks
setup_mocks()

# Now import the Flask app
with patch.dict('os.environ', {'JWT_SECRET': 'test_secret'}):
    from ui.backend.app import app

class AutoTuneTest(unittest.TestCase):
    """
    Tests for auto-tune functionality in the image upload process
    """
    
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Create a mock image file
        self.mock_image_data = b'mock image data'
        
        # Create a mock response for FGSM attack
        self.mock_attack_result = {
            'epsilon_used': 0.02,  # Note this is different from the manual setting
            'orig_class': 'cat',
            'orig_conf': 0.95,
            'adv_class': 'dog',
            'adv_conf': 0.7,
            'original_image': 'base64_encoded_image_data',
            'perturbation_image': 'base64_encoded_image_data',
            'adversarial_image': 'base64_encoded_image_data'
        }
        
        # Access the global mock FGSM instance
        import tests.upload.mock_setup as mock_setup
        mock_setup.mock_fgsm_instance.auto_tune_attack.return_value = self.mock_attack_result
        
        # Set up filesystem mocks
        self.file_mock_patcher = patch('builtins.open', create=True)
        self.mock_file = self.file_mock_patcher.start()
        
        self.remove_patcher = patch('os.remove')
        self.mock_remove = self.remove_patcher.start()
        
    def tearDown(self):
        self.file_mock_patcher.stop()
        self.remove_patcher.stop()
        
    def test_attack_with_auto_tune(self):
        """Test attack with auto-tuning enabled"""
        # Create test data with auto-tuning enabled
        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',  # This will be ignored with auto-tune
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
        
        # Parse the response JSON
        response_data = json.loads(response.data)
        
        # Verify it contains the expected fields
        self.assertEqual(response_data['epsilon_used'], 0.02)  # Should be the auto-tuned value
        self.assertEqual(response_data['orig_class'], 'cat')
        self.assertEqual(response_data['adv_class'], 'dog')
        
        # Import to check the mock was called
        import tests.upload.mock_setup as mock_setup
        
        # Verify auto_tune_attack was called instead of attack
        mock_setup.mock_fgsm_instance.auto_tune_attack.assert_called_once()
        mock_setup.mock_fgsm_instance.attack.assert_not_called()
        
    def test_auto_tune_parameter_parsing(self):
        """Test different ways of specifying auto-tune in the request"""
        # Different variations of 'true' that should be accepted
        auto_tune_variations = [
            'true', 'TRUE', 'True', 'tRuE', 'tRue'
        ]
        
        # Import to access mocks
        import tests.upload.mock_setup as mock_setup
        
        for auto_tune_value in auto_tune_variations:
            # Reset mock call counts
            mock_setup.mock_fgsm_instance.auto_tune_attack.reset_mock()
            mock_setup.mock_fgsm_instance.attack.reset_mock()
            
            # Create test data
            data = {
                'model': 'mobilenet_v2',
                'epsilon': '0.05',
                'autoTune': auto_tune_value
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
            
            # Check that auto_tune_attack was called
            mock_setup.mock_fgsm_instance.auto_tune_attack.assert_called_once()
            mock_setup.mock_fgsm_instance.attack.assert_not_called()

if __name__ == '__main__':
    unittest.main() 