import unittest
import sys
import os
import numpy as np
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock TensorFlow and other dependencies before importing FGSM
sys.modules['tensorflow'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Import FGSM after mocks are set up
from fgsm.fgsm import FGSM

class FGSMBasicTest(unittest.TestCase):
    """
    Basic tests for the FGSM (Fast Gradient Sign Method) implementation
    """
    
    def setUp(self):
        # Create a patched version of FGSM with mocked TensorFlow operations
        self.patcher = patch('fgsm.fgsm.tf')
        self.mock_tf = self.patcher.start()
        
        # Mock numpy
        self.np_patcher = patch('fgsm.fgsm.np')
        self.mock_np = self.np_patcher.start()
        
        # Mock PIL
        self.pil_patcher = patch('fgsm.fgsm.Image')
        self.mock_pil = self.pil_patcher.start()
        
        # Mock model and its methods
        self.mock_model = MagicMock()
        self.mock_decode_predictions = MagicMock()
        self.mock_preprocess_input = MagicMock()
        
        # Configure mock tf.keras to return our mock model
        self.mock_tf.keras.applications.MobileNetV2.return_value = self.mock_model
        self.mock_tf.keras.applications.mobilenet_v2.decode_predictions = self.mock_decode_predictions
        self.mock_tf.keras.applications.mobilenet_v2.preprocess_input = self.mock_preprocess_input
        
        # Set up more mock behaviors
        self.mock_tf.sign.return_value = np.array([[[1.0, -1.0, 1.0]]])
        self.mock_tf.argmax.return_value = np.array([42])
        self.mock_tf.one_hot.return_value = np.array([0, 0, 1, 0, 0])
        self.mock_tf.reshape.return_value = np.array([[0, 0, 1, 0, 0]])
        
        # Create a sample image tensor
        self.image_tensor = np.array([[[0.1, 0.2, 0.3]]])
        self.mock_tf.convert_to_tensor.return_value = self.image_tensor
        
        # Create a sample model output (class probabilities)
        self.sample_probs = np.array([[0.1, 0.2, 0.7, 0.0, 0.0]])
        
    def tearDown(self):
        self.patcher.stop()
        self.np_patcher.stop()
        self.pil_patcher.stop()
    
    def test_fgsm_initialization(self):
        """Test FGSM class initialization"""
        # Initialize FGSM with default parameters
        fgsm = FGSM(epsilon=0.05, model_name='mobilenet_v2')
        
        # Check if model was loaded correctly
        self.assertEqual(fgsm.model, self.mock_model)
        self.assertEqual(fgsm.epsilon, 0.05)
        self.assertEqual(fgsm.model_name, 'mobilenet_v2')
        self.assertEqual(fgsm.image_size, (224, 224))
    
    def test_load_model_mobilenet(self):
        """Test loading MobileNetV2 model"""
        fgsm = FGSM(model_name='mobilenet_v2')
        
        # Verify model is loaded with correct parameters
        self.mock_tf.keras.applications.MobileNetV2.assert_called_once_with(
            include_top=True, weights='imagenet'
        )
        
        # Verify model is set to non-trainable
        self.assertFalse(fgsm.model.trainable)
    
    def test_get_imagenet_label(self):
        """Test getting ImageNet label from probabilities"""
        fgsm = FGSM()
        
        # Configure mock to return sample predictions
        self.mock_decode_predictions.return_value = [[
            ('n12345', 'cat', 0.95)
        ]]
        
        # Call get_imagenet_label
        label_id, class_name, confidence = fgsm.get_imagenet_label(self.sample_probs)
        
        # Check results
        self.assertEqual(label_id, 'n12345')
        self.assertEqual(class_name, 'cat')
        self.assertEqual(confidence, 0.95)
        
        # Verify decode_predictions was called with correct parameters
        self.mock_decode_predictions.assert_called_once_with(self.sample_probs, top=1)
    
    @patch('fgsm.fgsm.tf.GradientTape')
    def test_create_adversarial_pattern(self, mock_gradient_tape):
        """Test creation of adversarial pattern"""
        # Set up the mock gradient tape and its returned gradient
        mock_tape = MagicMock()
        mock_gradient_tape.return_value.__enter__.return_value = mock_tape
        mock_tape.gradient.return_value = np.array([[[0.5, -0.3, 0.7]]])
        
        # Set up mock model prediction
        self.mock_model.return_value = self.sample_probs
        
        # Initialize FGSM
        fgsm = FGSM()
        
        # Call create_adversarial_pattern
        pattern = fgsm.create_adversarial_pattern(self.image_tensor, np.array([[0, 1, 0, 0, 0]]))
        
        # Verify tf.sign was called with the gradient
        self.mock_tf.sign.assert_called_once()
        
        # Check that the pattern is the sign of the gradient
        self.assertEqual(pattern.tolist(), [[[1.0, -1.0, 1.0]]])
    
    @patch('fgsm.fgsm.os.makedirs')
    def test_attack_basic_flow(self, mock_makedirs):
        """Test the basic flow of an attack"""
        # Configure mock model to predict sample probabilities
        self.mock_model.predict.return_value = self.sample_probs
        
        # Configure decode_predictions to return sample class 
        self.mock_decode_predictions.return_value = [[
            ('n12345', 'cat', 0.95)
        ]]
        
        # Mock create_adversarial_pattern
        with patch.object(FGSM, 'create_adversarial_pattern') as mock_create_pattern, \
             patch.object(FGSM, 'preprocess') as mock_preprocess, \
             patch.object(FGSM, 'display_attack_results') as mock_display:
            
            # Configure mocks
            mock_create_pattern.return_value = np.array([[[1.0, -1.0, 1.0]]])
            mock_preprocess.return_value = self.image_tensor
            
            # Initialize FGSM
            fgsm = FGSM()
            
            # Call attack
            fgsm.attack("dummy_image.jpg")
            
            # Verify preprocess was called
            mock_preprocess.assert_called_once_with("dummy_image.jpg")
            
            # Verify model.predict was called
            self.mock_model.predict.assert_called()
            
            # Verify create_adversarial_pattern was called
            mock_create_pattern.assert_called_once()
            
            # Verify display_attack_results was called
            mock_display.assert_called_once()
            
            # Verify output directory was created
            mock_makedirs.assert_called_once_with("fgsm_results", exist_ok=True)

if __name__ == '__main__':
    unittest.main() 