import pytest
from unittest.mock import MagicMock, AsyncMock
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

    async def mock_stream_generator():
        yield mock_stream_chunk1
        yield mock_stream_chunk2

    mock_openai_service = AsyncMock()
    mock_openai_service.chat_completion.return_value = mock_stream_generator()
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


def test_extract_timestamp(service):
    assert service._extract_timestamp("Look at [12.5]") == 12.5
    assert service._extract_timestamp("No timestamp here") is None
    assert service._extract_timestamp("[100]") == 100.0
