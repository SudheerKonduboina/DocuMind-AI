import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from backend.core.rate_limiting import rate_limit_middleware
from backend.config.settings import settings

@pytest.fixture
def mock_request():
    req = MagicMock(spec=Request)
    req.headers = {}
    req.client = MagicMock()
    req.client.host = "127.0.0.1"
    return req

@pytest.fixture
def mock_call_next():
    async def call_next(request):
        return Response(content="ok")
    return call_next

@pytest.mark.asyncio
async def test_rate_limit_disabled(mock_request, mock_call_next, monkeypatch):
    monkeypatch.setattr("backend.core.rate_limiting.settings.RATE_LIMIT_ENABLED", False)
    
    response = await rate_limit_middleware(mock_request, mock_call_next)
    
    assert response.body == b"ok"

@pytest.mark.asyncio
async def test_rate_limit_user_id_from_client(mock_request, mock_call_next, monkeypatch):
    monkeypatch.setattr("backend.core.rate_limiting.settings.RATE_LIMIT_ENABLED", True)
    
    mock_rate_limiter_cls = MagicMock()
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_allowed.return_value = True
    mock_rate_limiter.get_remaining.return_value = 99
    mock_rate_limiter_cls.return_value = mock_rate_limiter
    
    monkeypatch.setattr("backend.core.rate_limiting.RateLimiter", mock_rate_limiter_cls)
    
    response = await rate_limit_middleware(mock_request, mock_call_next)
    
    assert response.body == b"ok"
    assert response.headers["X-RateLimit-Remaining"] == "99"
    mock_rate_limiter.is_allowed.assert_called_with("127.0.0.1", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_PERIOD)

@pytest.mark.asyncio
async def test_rate_limit_user_id_from_header(mock_request, mock_call_next, monkeypatch):
    monkeypatch.setattr("backend.core.rate_limiting.settings.RATE_LIMIT_ENABLED", True)
    mock_request.headers = {"X-User-ID": "test_user"}
    
    mock_rate_limiter_cls = MagicMock()
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_allowed.return_value = True
    mock_rate_limiter.get_remaining.return_value = 99
    mock_rate_limiter_cls.return_value = mock_rate_limiter
    
    monkeypatch.setattr("backend.core.rate_limiting.RateLimiter", mock_rate_limiter_cls)
    
    response = await rate_limit_middleware(mock_request, mock_call_next)
    
    assert response.body == b"ok"
    mock_rate_limiter.is_allowed.assert_called_with("test_user", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_PERIOD)

@pytest.mark.asyncio
async def test_rate_limit_user_id_unknown(mock_request, mock_call_next, monkeypatch):
    monkeypatch.setattr("backend.core.rate_limiting.settings.RATE_LIMIT_ENABLED", True)
    mock_request.client = None
    
    mock_rate_limiter_cls = MagicMock()
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_allowed.return_value = True
    mock_rate_limiter.get_remaining.return_value = 99
    mock_rate_limiter_cls.return_value = mock_rate_limiter
    
    monkeypatch.setattr("backend.core.rate_limiting.RateLimiter", mock_rate_limiter_cls)
    
    await rate_limit_middleware(mock_request, mock_call_next)
    
    mock_rate_limiter.is_allowed.assert_called_with("unknown", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_PERIOD)

@pytest.mark.asyncio
async def test_rate_limit_exceeded(mock_request, mock_call_next, monkeypatch):
    monkeypatch.setattr("backend.core.rate_limiting.settings.RATE_LIMIT_ENABLED", True)
    
    mock_rate_limiter_cls = MagicMock()
    mock_rate_limiter = AsyncMock()
    mock_rate_limiter.is_allowed.return_value = False
    mock_rate_limiter.get_remaining.return_value = 0
    mock_rate_limiter_cls.return_value = mock_rate_limiter
    
    monkeypatch.setattr("backend.core.rate_limiting.RateLimiter", mock_rate_limiter_cls)
    
    with pytest.raises(HTTPException) as excinfo:
        await rate_limit_middleware(mock_request, mock_call_next)
        
    assert excinfo.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Rate limit exceeded" in excinfo.value.detail
    assert excinfo.value.headers["X-RateLimit-Remaining"] == "0"
