# Authentication Tests

This directory contains tests for the authentication system of the application.

## Setup

Before running the tests, make sure you have installed the required dependencies:

```bash
pip install flask-bcrypt pyjwt python-dotenv
```

## Running Tests

To run the authentication tests:

```bash
# From the project root directory
python tests/auth_test.py
```

## Troubleshooting Common Errors

### "No module named 'db'" Error

If you encounter an error saying "No module named 'db'", the test is fixed to handle this by mocking the db module. The test includes:

```python
# Mock the db module before importing auth
sys.modules['db'] = MagicMock()
sys.modules['db'].execute_query = MagicMock()
```

### "No module named 'dotenv'" Error

If you encounter an error with the dotenv module, the test mocks it:

```python
# Mock dotenv
sys.modules['dotenv'] = MagicMock()
sys.modules['dotenv'].load_dotenv = MagicMock()
```

### "No module named 'flask_bcrypt'" Error

If you get this error, install flask-bcrypt:

```bash
pip install flask-bcrypt
```

### JWT Token Issues

The test patches the JWT_SECRET environment variable to 'test_secret' to avoid errors related to missing environment variables.

## Test Structure

The `auth_test.py` file contains tests for the core authentication functions:

- **test_register_user_success**: Tests successful user registration
- **test_register_user_existing_email**: Tests registration with an email that already exists
- **test_login_user_success**: Tests successful login
- **test_login_user_invalid_email**: Tests login with an invalid email
- **test_verify_token_valid**: Tests verifying a valid token
- **test_verify_token_expired**: Tests verifying an expired token

## Mocking

The tests use mocking to avoid actual database operations:

- `execute_query` is mocked to simulate database access
- `bcrypt` is mocked for password hashing
- `jwt` is mocked for token generation and verification
- Environment variables like `JWT_SECRET` are patched
- The `db` module is mocked entirely
- The `dotenv` module is mocked to avoid loading from .env files

This ensures tests can run without a database connection and will always behave consistently. 