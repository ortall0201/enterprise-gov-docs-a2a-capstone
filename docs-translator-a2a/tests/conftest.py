"""
Pytest configuration for Docs Translator A2A tests.
"""

import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Set test API key if not already set
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test-api-key"

    # Set other test environment variables
    os.environ["LOG_LEVEL"] = "WARNING"  # Reduce logging noise in tests
    os.environ["A2A_SERVICE_PORT"] = "8001"
