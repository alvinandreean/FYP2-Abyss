import sys
from unittest.mock import MagicMock

# Create global mocks that will be shared across test files
mock_fgsm_instance = MagicMock()
mock_fgsm_class = MagicMock()
mock_fgsm_class.return_value = mock_fgsm_instance

def setup_mocks():
    """Set up all the mocks needed for the upload tests"""
    # Mock TensorFlow and other dependencies
    sys.modules['tensorflow'] = MagicMock()
    sys.modules['matplotlib'] = MagicMock()
    sys.modules['matplotlib.pyplot'] = MagicMock()
    
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
    
    return {
        'fgsm_instance': mock_fgsm_instance,
        'fgsm_class': mock_fgsm_class
    } 