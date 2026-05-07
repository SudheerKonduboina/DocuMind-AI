import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import asyncio
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Setup env variables before anything else
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["XAI_API_KEY"] = "test-key"
os.environ["AWS_ACCESS_KEY_ID"] = "test-aws"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test-aws-secret"

try:
    from backend.main import app
except ImportError:
    try:
        from main import app
    except ImportError:
        app = MagicMock()

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def async_client():
    from httpx import AsyncClient
    return AsyncClient(app=app, base_url="http://test")
