# FGSM Tests

This directory contains tests for the Fast Gradient Sign Method (FGSM) implementation.

## Setup

Before running the tests, make sure you have installed the required dependencies:

```bash
pip install numpy
pip install tensorflow  # Not actually used in tests but needed for imports
```

## Running Tests

To run the FGSM tests:

```bash
# From the project root directory
python tests/fgsm_basic_test.py
```

## Test Structure

The `fgsm_basic_test.py` file contains basic tests for the FGSM implementation:

- **test_fgsm_initialization**: Verifies that the FGSM class initializes correctly
- **test_load_model_mobilenet**: Tests the model loading functionality
- **test_get_imagenet_label**: Tests the ImageNet label extraction
- **test_create_adversarial_pattern**: Tests the creation of adversarial pattern using gradient
- **test_attack_basic_flow**: Tests the basic flow of an attack

## Mocking

The tests use extensive mocking to avoid actually loading TensorFlow models:

- `tensorflow` is mocked to avoid needing an actual GPU/TPU
- `matplotlib` is mocked to avoid creating actual plots
- `PIL` is mocked to avoid file system operations
- Model loading and prediction functions are mocked

This ensures tests run quickly and don't depend on external libraries or GPU resources.

## Note on Test Design

These tests are designed to verify the logical flow and function calls in the FGSM implementation, not the actual adversarial attack effectiveness. For that, you would need integration tests with real models and images.

The tests focus on:

1. Correct function call sequences
2. Proper parameter passing
3. Basic logic of the FGSM algorithm

For a full evaluation of the adversarial attack performance, you should run the actual FGSM implementation on test images and evaluate the results. 