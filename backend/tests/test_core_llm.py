import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
import importlib
import backend.core.llm

@pytest.fixture(autouse=True)
def reset_llm_module():
    # Store original client
    original_client = getattr(backend.core.llm, 'client', None)
    yield
    # Restore original client
    backend.core.llm.client = original_client

@pytest.mark.asyncio
async def test_ask_llm_no_client(monkeypatch):
    backend.core.llm.client = None
    with pytest.raises(ValueError, match="XAI_API_KEY not configured"):
        await backend.core.llm.ask_llm("test")

@pytest.mark.asyncio
async def test_ask_llm_success(monkeypatch):
    mock_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "LLM Response"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    
    backend.core.llm.client = mock_client
    
    res = await backend.core.llm.ask_llm("test prompt")
    assert res == "LLM Response"

@pytest.mark.asyncio
async def test_chat_completion_no_client(monkeypatch):
    backend.core.llm.client = None
    with pytest.raises(ValueError, match="XAI_API_KEY not configured"):
        await backend.core.llm.chat_completion([{"role": "user", "content": "test"}])

@pytest.mark.asyncio
async def test_chat_completion_success_no_stream(monkeypatch):
    mock_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Chat Response"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    
    backend.core.llm.client = mock_client
    
    res = await backend.core.llm.chat_completion([{"role": "user", "content": "test"}])
    assert res == "Chat Response"

@pytest.mark.asyncio
async def test_chat_completion_success_stream(monkeypatch):
    mock_client = AsyncMock()
    # For stream, the returned response is the stream object itself
    mock_stream_obj = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_stream_obj
    
    backend.core.llm.client = mock_client
    
    res = await backend.core.llm.chat_completion([{"role": "user", "content": "test"}], stream=True)
    assert res == mock_stream_obj

def test_llm_init_no_api_key(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "")
    
    # Reload the module to trigger the initialization logic
    import backend.core.llm as llm_module
    importlib.reload(llm_module)
    
    assert getattr(llm_module, 'client', None) is None
    
    # Reload back with a fake key to not break other tests
    monkeypatch.setenv("XAI_API_KEY", "fake_key")
    importlib.reload(llm_module)
