import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from backend.modules.chatbot.chatbot_service import ChatbotService
import json
import uuid


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    service = ChatbotService(db=mock_db)
    service.chat_repo = MagicMock()
    service.message_repo = MagicMock()
    service.chunk_repo = MagicMock()
    service.segment_repo = MagicMock()
    service.cache_service = AsyncMock()
    return service


def test_get_chat_not_found(service):
    service.chat_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_chat(str(uuid.uuid4()), str(uuid.uuid4()))
    assert excinfo.value.status_code == 404


def test_delete_chat_not_found(service):
    service.chat_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.delete_chat(str(uuid.uuid4()), str(uuid.uuid4()))
    assert excinfo.value.status_code == 404


def test_get_messages_not_found(service):
    service.chat_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_messages(str(uuid.uuid4()), str(uuid.uuid4()))
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_send_message_chat_not_found(service):
    service.chat_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        async for _ in service.send_message(
            str(uuid.uuid4()), "hello", str(uuid.uuid4())
        ):
            pass
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_send_message_cached(service):
    mock_chat = MagicMock()
    service.chat_repo.get_by_id.return_value = mock_chat

    cached_data = {"tokens": ["Hello", " world"], "metadata": {}}
    service.cache_service.get.return_value = json.dumps(cached_data)

    chunks = []
    async for chunk in service.send_message(
        str(uuid.uuid4()), "hello", str(uuid.uuid4())
    ):
        chunks.append(chunk)

    assert len(chunks) == 3  # 2 tokens + 1 done chunk
    assert chunks[0].token == "Hello"
    assert chunks[2].done is True


@pytest.mark.asyncio
async def test_send_message_not_cached(service, monkeypatch):
    mock_chat = MagicMock()
    mock_chat.document_id = str(uuid.uuid4())
    service.chat_repo.get_by_id.return_value = mock_chat
    service.cache_service.get.return_value = None

    msg = MagicMock()
    msg.role = "user"
    msg.content = "hi"
    service.message_repo.get_by_chat.return_value = [msg]

    # Mock retrieve_context
    async def mock_retrieve_context(*args, **kwargs):
        return "context text", 10.0, "doc1"

    service._retrieve_context = mock_retrieve_context

    # Mock stream response
    mock_stream_chunk1 = MagicMock()
    mock_stream_chunk1.choices = [MagicMock()]
    mock_stream_chunk1.choices[0].delta.content = "Response [10.5]"

    mock_stream_chunk2 = MagicMock()
    mock_stream_chunk2.choices = [MagicMock()]
    mock_stream_chunk2.choices[0].delta.content = ""  # Empty

    async def mock_stream_generator(*args, **kwargs):
        yield mock_stream_chunk1
        yield mock_stream_chunk2

    mock_openai_service = MagicMock()
    mock_openai_service.chat_completion = AsyncMock(side_effect=mock_stream_generator)
    monkeypatch.setattr(
        "backend.modules.chatbot.chatbot_service.openai_service", mock_openai_service
    )

    chunks = []
    async for chunk in service.send_message(
        str(uuid.uuid4()), "hello", str(uuid.uuid4())
    ):
        chunks.append(chunk)

    assert len(chunks) == 2  # 1 content chunk + 1 done chunk
    assert chunks[0].token == "Response [10.5]"
    assert chunks[0].timestamp == 10.5
    assert chunks[1].done is True


@pytest.mark.asyncio
async def test_retrieve_context_no_results(service, mock_db):
    # Mocking DB query return empty list
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
        []
    )
    # Mock for document file type check
    mock_db.query.return_value.filter.return_value.first.return_value = None

    context, ts, doc = await service._retrieve_context(
        str(uuid.uuid4()), "query", str(uuid.uuid4())
    )
    assert context == ""
    assert ts is None
    assert doc is None


@pytest.mark.asyncio
async def test_retrieve_context_with_results(service, mock_db):
    mock_chunk = MagicMock()
    mock_chunk.content = "chunk content"
    mock_chunk.document_id = "doc1"
    mock_chunk.chunk_index = 0

    # Mocking DB query return list with chunk
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
        mock_chunk
    ]
    # Mock for document file type check (PDF)
    mock_doc = MagicMock()
    mock_doc.file_type = "pdf"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_doc

    doc_id = str(uuid.uuid4())
    context, ts, doc = await service._retrieve_context(
        doc_id, "query", str(uuid.uuid4())
    )
    assert context == "chunk content"
    assert ts is None
    assert doc == doc_id


@pytest.mark.asyncio
async def test_send_message_truncate(service, monkeypatch):
    mock_chat = MagicMock()
    service.chat_repo.get_by_id.return_value = mock_chat
    service.cache_service.get.return_value = None
    service.message_repo.get_by_chat.return_value = []

    # Mock retrieve_context and openai
    service._retrieve_context = AsyncMock(return_value=("", None, None))

    async def mock_stream_generator(*args, **kwargs):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "test"
        yield chunk

    mock_openai = MagicMock()
    mock_openai.chat_completion = AsyncMock(side_effect=mock_stream_generator)
    monkeypatch.setattr(
        "backend.modules.chatbot.chatbot_service.openai_service", mock_openai
    )

    long_content = "a" * (service.MAX_MESSAGE_LENGTH * 3)
    async for _ in service.send_message(
        str(uuid.uuid4()), long_content, str(uuid.uuid4())
    ):
        pass

    # Verify create_with_metadata was called with truncated content
    call_args = service.message_repo.create_with_metadata.call_args_list
    assert "...[message truncated]" in call_args[0][0][2]


@pytest.mark.asyncio
async def test_send_message_cache_error(service, monkeypatch):
    mock_chat = MagicMock()
    service.chat_repo.get_by_id.return_value = mock_chat
    service.cache_service.get.side_effect = Exception("Redis down")
    service.message_repo.get_by_chat.return_value = []

    # Mock retrieve_context and openai
    service._retrieve_context = AsyncMock(return_value=("", None, None))

    async def mock_stream_generator(*args, **kwargs):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "test"
        yield chunk

    mock_openai = MagicMock()
    mock_openai.chat_completion = AsyncMock(side_effect=mock_stream_generator)
    monkeypatch.setattr(
        "backend.modules.chatbot.chatbot_service.openai_service", mock_openai
    )

    async for _ in service.send_message(str(uuid.uuid4()), "hi", str(uuid.uuid4())):
        pass

    # Should proceed despite cache error
    assert service.message_repo.create_with_metadata.called


@pytest.mark.asyncio
async def test_send_message_token_limit(service, monkeypatch):
    mock_chat = MagicMock()
    service.chat_repo.get_by_id.return_value = mock_chat
    service.cache_service.get.return_value = None

    # Create enough history to trigger truncation
    msg = MagicMock()
    msg.role = "user"
    msg.content = "long history " * 500
    service.message_repo.get_by_chat.return_value = [msg] * 5

    service._retrieve_context = AsyncMock(
        return_value=("very long context " * 500, None, "doc1")
    )

    async def mock_stream_generator(*args, **kwargs):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "test"
        yield chunk

    mock_openai = MagicMock()
    mock_openai.chat_completion = AsyncMock(side_effect=mock_stream_generator)
    monkeypatch.setattr(
        "backend.modules.chatbot.chatbot_service.openai_service", mock_openai
    )

    async for _ in service.send_message(str(uuid.uuid4()), "hi", str(uuid.uuid4())):
        pass

    # Verify it completed (meaning truncation logic was exercised)
    assert mock_openai.chat_completion.called


@pytest.mark.asyncio
async def test_retrieve_context_audio_video(service, mock_db):
    doc_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    mock_doc = MagicMock()
    mock_doc.file_type = "audio"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_doc

    # Mock transcript and segments
    mock_transcript = MagicMock()
    mock_transcript.id = str(uuid.uuid4())

    mock_segment = MagicMock()
    mock_segment.start_time = 10.0
    mock_segment.content = "audio content"

    # Using patch to mock the internal imports/repos
    with patch(
        "backend.modules.media.media_repository.TranscriptRepository"
    ) as mock_t_repo, patch(
        "backend.modules.media.media_repository.TranscriptSegmentRepository"
    ) as mock_s_repo:

        mock_t_repo.return_value.get_by_document.return_value = mock_transcript
        mock_s_repo.return_value.get_by_transcript.return_value = [mock_segment]

        context, ts, doc = await service._retrieve_context(doc_id, "query", user_id)

        assert "[10.0s] audio content" in context
        assert ts == 10.0
        assert doc == doc_id


@pytest.mark.asyncio
async def test_send_message_cache_load_error(service, monkeypatch):
    mock_chat = MagicMock()
    service.chat_repo.get_by_id.return_value = mock_chat
    service.cache_service.get.return_value = "invalid json"
    service.message_repo.get_by_chat.return_value = []

    # Mock retrieve_context and openai to continue after cache load error
    service._retrieve_context = AsyncMock(return_value=("", None, None))

    async def mock_stream_generator(*args, **kwargs):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "test"
        yield chunk

    mock_openai = MagicMock()
    mock_openai.chat_completion = AsyncMock(side_effect=mock_stream_generator)
    monkeypatch.setattr(
        "backend.modules.chatbot.chatbot_service.openai_service", mock_openai
    )

    async for _ in service.send_message(str(uuid.uuid4()), "hi", str(uuid.uuid4())):
        pass
    assert mock_openai.chat_completion.called


@pytest.mark.asyncio
async def test_send_message_cache_set_error(service, monkeypatch):
    mock_chat = MagicMock()
    service.chat_repo.get_by_id.return_value = mock_chat
    service.cache_service.get.return_value = None
    service.message_repo.get_by_chat.return_value = []
    service.cache_service.set.side_effect = Exception("Redis write fail")

    service._retrieve_context = AsyncMock(return_value=("", None, None))

    async def mock_stream_generator(*args, **kwargs):
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "test"
        yield chunk

    mock_openai = MagicMock()
    mock_openai.chat_completion = AsyncMock(side_effect=mock_stream_generator)
    monkeypatch.setattr(
        "backend.modules.chatbot.chatbot_service.openai_service", mock_openai
    )

    async for _ in service.send_message(str(uuid.uuid4()), "hi", str(uuid.uuid4())):
        pass

    assert service.cache_service.set.called


@pytest.mark.asyncio
async def test_retrieve_context_no_transcript(service, mock_db):
    doc_id = str(uuid.uuid4())
    mock_doc = MagicMock()
    mock_doc.file_type = "audio"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_doc

    with patch(
        "backend.modules.media.media_repository.TranscriptRepository"
    ) as mock_t_repo:
        mock_t_repo.return_value.get_by_document.return_value = None
        context, ts, doc = await service._retrieve_context(
            doc_id, "query", str(uuid.uuid4())
        )
        assert context == ""


def test_extract_timestamp(service):
    assert service._extract_timestamp("Look at [12.5]") == 12.5
    assert service._extract_timestamp("No timestamp here") is None
    assert service._extract_timestamp("[100]") == 100.0
