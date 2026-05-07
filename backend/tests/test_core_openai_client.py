import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch
import importlib
import backend.core.openai_client
from backend.core.openai_client import OpenAIService


@pytest.fixture(autouse=True)
def reset_openai_module():
    # Store original client
    original_client = getattr(backend.core.openai_client, "client", None)
    yield
    # Restore original client
    backend.core.openai_client.client = original_client
    backend.core.openai_client.openai_service = OpenAIService(original_client)


@pytest.mark.asyncio
async def test_generate_embedding_no_client():
    service = OpenAIService(None)
    with pytest.raises(ValueError, match="XAI_API_KEY not configured"):
        await service.generate_embedding("test")


@pytest.mark.asyncio
async def test_generate_embedding_success():
    mock_client = AsyncMock()
    mock_data = MagicMock()
    mock_data.embedding = [0.1, 0.2]
    mock_response = MagicMock()
    mock_response.data = [mock_data]
    mock_client.embeddings.create.return_value = mock_response

    service = OpenAIService(mock_client)
    res = await service.generate_embedding("test")
    assert res == [0.1, 0.2]


@pytest.mark.asyncio
async def test_generate_embeddings_batch_no_client():
    service = OpenAIService(None)
    with pytest.raises(ValueError, match="XAI_API_KEY not configured"):
        await service.generate_embeddings_batch(["test"])


@pytest.mark.asyncio
async def test_generate_embeddings_batch_success():
    mock_client = AsyncMock()
    mock_data1 = MagicMock()
    mock_data1.embedding = [0.1, 0.2]
    mock_data2 = MagicMock()
    mock_data2.embedding = [0.3, 0.4]
    mock_response = MagicMock()
    mock_response.data = [mock_data1, mock_data2]
    mock_client.embeddings.create.return_value = mock_response

    service = OpenAIService(mock_client)
    res = await service.generate_embeddings_batch(["test1", "test2"])
    assert res == [[0.1, 0.2], [0.3, 0.4]]


@pytest.mark.asyncio
async def test_chat_completion_no_client():
    service = OpenAIService(None)
    with pytest.raises(ValueError, match="XAI_API_KEY not configured"):
        await service.chat_completion([{"role": "user", "content": "test"}])


@pytest.mark.asyncio
async def test_chat_completion_success_no_stream():
    mock_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Response"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAIService(mock_client)
    res = await service.chat_completion([{"role": "user", "content": "test"}])
    assert res == "Response"


@pytest.mark.asyncio
async def test_chat_completion_success_stream():
    mock_client = AsyncMock()
    mock_stream = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_stream

    service = OpenAIService(mock_client)
    res = await service.chat_completion(
        [{"role": "user", "content": "test"}], stream=True
    )
    assert res == mock_stream


@pytest.mark.asyncio
async def test_transcribe_audio_no_client():
    service = OpenAIService(None)
    with pytest.raises(ValueError, match="XAI_API_KEY not configured"):
        await service.transcribe_audio("test.mp3")


@pytest.mark.asyncio
async def test_transcribe_audio_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "Transcription text"
    mock_client.audio.transcriptions.create.return_value = mock_response

    service = OpenAIService(mock_client)

    m = mock_open(read_data=b"data")
    with patch("builtins.open", m):
        res = await service.transcribe_audio("test.mp3")

    assert res == "Transcription text"


@pytest.mark.asyncio
async def test_summarize_text_success():
    mock_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Summary"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAIService(mock_client)
    res = await service.summarize_text("Long text")
    assert res == "Summary"


def test_openai_init_no_api_key(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "")
    import backend.core.openai_client as module

    importlib.reload(module)
    assert module.client is None

    monkeypatch.setenv("XAI_API_KEY", "fake_key")
    importlib.reload(module)
