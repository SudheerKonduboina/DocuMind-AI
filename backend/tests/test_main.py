import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import MagicMock, patch


def test_health_check_success():
    with patch("backend.main.engine.connect"), patch("backend.main.redis_client.ping"):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_health_check_redis_fail():
    with patch("backend.main.engine.connect"), patch(
        "backend.main.redis_client.ping", side_effect=Exception("Redis down")
    ):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["redis"] == "disconnected"


def test_health_check_database_fail():
    with patch("backend.main.engine.connect", side_effect=Exception("DB down")):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_lifespan_startup_error():
    from backend.main import lifespan

    mock_app = MagicMock()

    with patch(
        "backend.main.engine.connect", side_effect=Exception("Startup DB fail")
    ), pytest.raises(Exception):
        async with lifespan(mock_app):
            pass
