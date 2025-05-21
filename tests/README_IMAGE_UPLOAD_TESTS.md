# Image Upload Tests

This directory contains tests for the image upload functionality of the FGSM attack endpoint.

## Setup

Before running the tests, make sure you have installed the required dependencies:

```bash
pip install flask
pip install flask-bcrypt
pip install pyjwt
pip install python-dotenv
```

## Running Tests

To run the image upload tests:

```bash
# From the project root directory
python tests/image_upload_test.py
```

## Test Structure

The `image_upload_test.py` file contains tests for the image upload API endpoint:

- **test_attack_with_valid_image_upload**: Tests that valid image uploads for FGSM attacks are processed correctly
- **test_attack_missing_image**: Tests the error handling when an image is not provided
- **test_attack_missing_model**: Tests the error handling when a model is not specified
- **test_attack_with_auto_tune**: Tests that auto-tuning mode is properly activated when requested

## Mocking

The tests use extensive mocking to avoid actual file operations and model loading:

- `tensorflow`, `matplotlib`, and other dependencies are mocked
- The FGSM class is mocked to return predefined results
- File system operations (opening files, removing files) are mocked
- All database operations are mocked

## API Testing Approach

These tests focus on the API interface itself:

1. Test correct parameter handling
2. Test form data and file upload processing
3. Test response structure and codes
4. Test error conditions

By mocking the underlying FGSM implementation, these tests can verify the API contract without needing to actually run ML models or process real images.

## Integration with Other Tests

This test complements the FGSM basic tests:
- FGSM tests verify the algorithm works correctly
- Image upload tests verify the API handles uploads correctly

Together, they provide coverage of both the core functionality and the user-facing API. 