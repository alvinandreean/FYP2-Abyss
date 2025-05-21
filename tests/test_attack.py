import unittest
import sys
import os
import io
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Set up mocks for dependencies
mock_fgsm_instance = MagicMock()
mock_fgsm_class = MagicMock()
mock_fgsm_class.return_value = mock_fgsm_instance

# Define dictionary return values for attack functions
regular_attack_result = {
    'epsilon_used': 0.05,
    'orig_class': 'cat',
    'orig_conf': 0.95,
    'adv_class': 'dog',
    'adv_conf': 0.7,
    'original_image': 'base64_encoded_regular_image',
    'perturbation_image': 'base64_encoded_regular_perturbation',
    'adversarial_image': 'base64_encoded_regular_adversarial'
}

auto_tune_attack_result = {
    'epsilon_used': 0.02,
    'orig_class': 'cat',
    'orig_conf': 0.95,
    'adv_class': 'dog',
    'adv_conf': 0.7,
    'original_image': 'base64_encoded_auto_tune_image',
    'perturbation_image': 'base64_encoded_auto_tune_perturbation',
    'adversarial_image': 'base64_encoded_auto_tune_adversarial'
}

# Configure return values for the mock instance
mock_fgsm_instance.attack.return_value = regular_attack_result
mock_fgsm_instance.auto_tune_attack.return_value = auto_tune_attack_result

# Mock modules before importing Flask app

sys.modules['fgsm'] = MagicMock(FGSM=mock_fgsm_class)
sys.modules['db'] = MagicMock()
sys.modules['jwt'] = MagicMock()
sys.modules['flask_bcrypt'] = MagicMock()
sys.modules['auth'] = MagicMock()

# Import the Flask app
with patch.dict('os.environ', {'JWT_SECRET': 'test_secret'}):
    from ui.backend.app import app

class AttackTest(unittest.TestCase):
    """Tests for both regular and auto-tune attack functionality"""
    
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Create a mock image file
        self.mock_image_data = b'mock image data'
        
        # Set up file system mocks
        self.file_mock_patcher = patch('builtins.open', create=True)
        self.mock_file = self.file_mock_patcher.start()
        self.mock_file.return_value.__enter__.return_value.read.return_value = self.mock_image_data
        
        self.remove_patcher = patch('os.remove')
        self.mock_remove = self.remove_patcher.start()
        
    def tearDown(self):
        self.file_mock_patcher.stop()
        self.remove_patcher.stop()
        
    def test_attack_without_auto_tune(self):
        """Test regular attack without auto-tuning"""
        # Reset mocks
        mock_fgsm_instance.attack.reset_mock()
        mock_fgsm_instance.auto_tune_attack.reset_mock()
        
        # Create request data
        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',
            'autoTune': 'false',
            'image': (io.BytesIO(self.mock_image_data), 'test_image.jpg')
        }
        
        # Send request to the API
        response = self.client.post('/attack', data=data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['epsilon_used'], 0.05)
        self.assertEqual(response_data['orig_class'], 'cat')
        self.assertEqual(response_data['adv_class'], 'dog')
        self.assertEqual(response_data['original_image'], 'base64_encoded_regular_image')
        
        # Verify the right method was called
        mock_fgsm_instance.attack.assert_called_once()
        mock_fgsm_instance.auto_tune_attack.assert_not_called()
    
    def test_attack_with_auto_tune(self):
        """Test attack with auto-tuning enabled"""
        # Reset mocks
        mock_fgsm_instance.attack.reset_mock()
        mock_fgsm_instance.auto_tune_attack.reset_mock()
        
        # Create request data
        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',  # This will be ignored with auto-tune
            'autoTune': 'true',
            'image': (io.BytesIO(self.mock_image_data), 'test_image.jpg')
        }
        
        # Send request to the API
        response = self.client.post('/attack', data=data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['epsilon_used'], 0.02)  # Should be the auto-tuned value
        self.assertEqual(response_data['orig_class'], 'cat')
        self.assertEqual(response_data['adv_class'], 'dog')
        self.assertEqual(response_data['original_image'], 'base64_encoded_auto_tune_image')
        
        # Verify the right method was called
        mock_fgsm_instance.auto_tune_attack.assert_called_once()
        mock_fgsm_instance.attack.assert_not_called()
        
    def test_different_models(self):
        """Test different model types for attacks"""
        # List of models to test
        models = ['mobilenet_v2', 'inception_v3']
        
        model_specific_results = {
            'mobilenet_v2': {
                'orig_class': 'cat',
                'adv_class': 'dog'
            },
            'inception_v3': {
                'orig_class': 'cat',
                'adv_class': 'tiger'
            }
        }
        
        for model_name in models:
            # Reset mocks
            mock_fgsm_class.reset_mock()
            mock_fgsm_instance.attack.reset_mock()
            
            # Set up model-specific results
            model_result = regular_attack_result.copy()
            model_result['adv_class'] = model_specific_results[model_name]['adv_class']
            mock_fgsm_instance.attack.return_value = model_result
            
            # Create request data with specific model
            data = {
                'model': model_name,
                'epsilon': '0.05',
                'autoTune': 'false',
                'image': (io.BytesIO(self.mock_image_data), 'test_image.jpg')
            }
            
            # Make the request
            response = self.client.post('/attack', data=data)
            
            # Check the response
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['adv_class'], model_specific_results[model_name]['adv_class'], 
                            f"Model {model_name} should predict {model_specific_results[model_name]['adv_class']}")
            
            # Verify FGSM was initialized with the correct model name
            mock_fgsm_class.assert_called_once()
            call_args = mock_fgsm_class.call_args[1]
            self.assertEqual(call_args['model_name'], model_name)
    
    def test_different_epsilon_values(self):
        """Test different epsilon values for regular attacks"""
        # List of epsilon values to test
        epsilon_values = ['0.01', '0.05', '0.1', '0.2', '0.5']
        
        for epsilon in epsilon_values:
            # Reset mocks
            mock_fgsm_class.reset_mock()
            mock_fgsm_instance.attack.reset_mock()
            
            # Create epsilon-specific result 
            epsilon_result = regular_attack_result.copy()
            epsilon_result['epsilon_used'] = float(epsilon)
            mock_fgsm_instance.attack.return_value = epsilon_result
            
            # Create request data with specific epsilon
            data = {
                'model': 'mobilenet_v2',
                'epsilon': epsilon,
                'autoTune': 'false',
                'image': (io.BytesIO(self.mock_image_data), 'test_image.jpg')
            }
            
            # Make the request
            response = self.client.post('/attack', data=data)
            
            # Check the response
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['epsilon_used'], float(epsilon))
            
            # Verify FGSM was initialized with the correct epsilon value
            mock_fgsm_class.assert_called_once()
            call_args = mock_fgsm_class.call_args[1]
            self.assertEqual(call_args['epsilon'], float(epsilon))

if __name__ == '__main__':
    unittest.main() 