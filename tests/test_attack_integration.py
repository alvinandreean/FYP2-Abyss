import unittest
import io
from unittest.mock import patch, MagicMock
import base64

import sys, os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from ui.backend.app import app  # Adjust if needed

class AttackIntegrationTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.test_image_data = b'test image bytes'
        self.mock_file = io.BytesIO(self.test_image_data)
        
        # Setup mock for FGSM
        self.patcher = patch('ui.backend.app.FGSM')
        self.mock_fgsm_class = self.patcher.start()
        self.mock_instance = MagicMock()
        
        # Mock successful attack results
        self.mock_instance.attack.return_value = {
            'orig_class': 'dog',
            'adv_class': 'cat',
            'confidence': 0.85,
            'epsilon_used': 0.05,
            'orig_image': 'base64_encoded_image',
            'adv_image': 'base64_encoded_image'
        }
        
        # Mock successful auto-tune attack results
        self.mock_instance.auto_tune_attack.return_value = {
            'orig_class': 'dog',
            'adv_class': 'cat',
            'confidence': 0.85,
            'epsilon_used': 0.02,  # Auto-tuned value
            'orig_image': 'base64_encoded_image',
            'adv_image': 'base64_encoded_image'
        }
        
        self.mock_fgsm_class.return_value = self.mock_instance
        
        # Mock requests.get for URL-based tests
        self.requests_patcher = patch('requests.get')
        self.mock_requests_get = self.requests_patcher.start()
        mock_response = MagicMock()
        mock_response.content = self.test_image_data
        self.mock_requests_get.return_value = mock_response
        
        # Mock Image.open for PIL
        self.pil_patcher = patch('PIL.Image.open')
        self.mock_pil_open = self.pil_patcher.start()
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        mock_image.save.return_value = None
        self.mock_pil_open.return_value = mock_image

    def tearDown(self):
        self.patcher.stop()
        self.requests_patcher.stop()
        self.pil_patcher.stop()

    def _print_test_header(self, test_name):
        print("\n" + "="*50)
        print(f"START TEST: {test_name}")
        print("="*50)

    def _print_test_footer(self, test_name, passed=True):
        status = "PASSED" if passed else "FAILED"
        print("="*50)
        print(f"END TEST: {test_name} - {status}")
        print("="*50 + "\n")

    # --------- /attack tests -----------

    def test_attack_regular_success(self):
        test_name = "Regular Attack Success"
        self._print_test_header(test_name)

        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',
            'autoTune': 'false'
        }
        data['image'] = (io.BytesIO(self.test_image_data), 'test.jpg')
        response = self.client.post('/attack', data=data, content_type='multipart/form-data')
        
        try:
            self.assertEqual(response.status_code, 200)
            result = response.get_json()
            self.assertIn('epsilon_used', result)
            self.assertEqual(result['epsilon_used'], 0.05)
            self.assertIn('orig_class', result)
            self.assertIn('adv_class', result)
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_attack_auto_tune_success(self):
        test_name = "Auto-tune Attack Success"
        self._print_test_header(test_name)

        data = {
            'model': 'mobilenet_v2',
            'epsilon': '0.05',  # ignored with autoTune true
            'autoTune': 'true'
        }
        data['image'] = (io.BytesIO(self.test_image_data), 'test.jpg')
        response = self.client.post('/attack', data=data, content_type='multipart/form-data')
        
        try:
            self.assertEqual(response.status_code, 200)
            result = response.get_json()
            self.assertEqual(result['epsilon_used'], 0.02)
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    # --------- /attack-from-url tests -----------

    def test_attack_from_url_regular_success(self):
        test_name = "Attack From URL Regular Success"
        self._print_test_header(test_name)

        payload = {
            'imageUrl': 'example.url/image.jpg',
            'model': 'mobilenet_v2',
            'epsilon': 0.05,
            'autoTune': False
        }
        response = self.client.post('/attack-from-url', json=payload)
        
        try:
            self.assertEqual(response.status_code, 200)
            result = response.get_json()
            self.assertIn('epsilon_used', result)
            self.assertEqual(result['epsilon_used'], 0.05)
            self.assertIn('orig_class', result)
            self.assertIn('adv_class', result)
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

    def test_attack_from_url_auto_tune_success(self):
        test_name = "Attack From URL Auto-tune Success"
        self._print_test_header(test_name)

        payload = {
            'imageUrl': 'example.url/image.jpg',
            'model': 'mobilenet_v2',
            'epsilon': 0.05,  # ignored with autoTune
            'autoTune': True
        }
        response = self.client.post('/attack-from-url', json=payload)
        
        try:
            self.assertEqual(response.status_code, 200)
            result = response.get_json()
            self.assertEqual(result['epsilon_used'], 0.02)
            self._print_test_footer(test_name, True)
        except Exception as e:
            self._print_test_footer(test_name, False)
            raise e

if __name__ == '__main__':
    unittest.main(verbosity=2)
