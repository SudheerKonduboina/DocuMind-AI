import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from backend.modules.chatbot.chatbot_service import ChatbotService
from backend.modules.chatbot.chatbot_schemas import ChatCreate
import json

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
        service.get_chat("chat1", "user1")
    assert excinfo.value.status_code == 404

def test_delete_chat_not_found(service):
    service.chat_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.delete_chat("chat1", "user1")
    assert excinfo.value.status_code == 404

def test_get_messages_not_found(service):
    service.chat_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_messages("chat1", "user1")
    assert excinfo.value.status_code == 404

@pytest.mark.asyncio
async def test_send_message_chat_not_found(service):
    service.chat_repo.get_by_id.return_value = None
    
    with pytest.raises(HTTPException) as excinfo:
        async for _ in service.send_message("chat1", "hello", "user1"):
            pass
    assert excinfo.value.status_code == 404

@pytest.mark.asyncio
async def test_send_message_cached(service):
    mock_chat = MagicMock()
    service.chat_repo.get_by_id.return_value = mock_chat
    
    cached_data = {"tokens": ["Hello", " world"], "metadata": {}}
    service.cache_service.get.return_value = json.dumps(cached_data)
    
    chunks = []
    async for chunk in service.send_message("chat1", "hello", "user1"):
        chunks.append(chunk)
        
    assert len(chunks) == 3 # 2 tokens + 1 done chunk
    assert chunks[0].token == "Hello"
    assert chunks[2].done is True

@pytest.mark.asyncio
async def test_send_message_not_cached(service, monkeypatch):
    mock_chat = MagicMock()
    mock_chat.document_id = "doc1"
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
    mock_stream_chunk2.choices[0].delta.content = "" # Empty
    
    async def mock_stream_generator():
        yield mock_stream_chunk1
        yield mock_stream_chunk2
        
    mock_openai_service = AsyncMock()
    mock_openai_service.chat_completion.return_value = mock_stream_generator()
    monkeypatch.setattr("backend.modules.chatbot.chatbot_service.openai_service", mock_openai_service)
    
    chunks = []
    async for chunk in service.send_message("chat1", "hello", "user1"):
        chunks.append(chunk)
        
    assert len(chunks) == 2 # 1 content chunk + 1 done chunk
    assert chunks[0].token == "Response [10.5]"
    assert chunks[0].timestamp == 10.5
    assert chunks[1].done is True

@pytest.mark.asyncio
async def test_retrieve_context_no_results(service, monkeypatch):
    mock_vector_service = MagicMock()
    mock_vector_service_instance = AsyncMock()
    mock_vector_service_instance.search.return_value = []
    mock_vector_service.return_value = mock_vector_service_instance
    monkeypatch.setattr("backend.modules.chatbot.chatbot_service.VectorSearchService", mock_vector_service)
    
    context, ts, doc = await service._retrieve_context("doc1", "query")
    assert context == ""
    assert ts is None
    assert doc is None

@pytest.mark.asyncio
async def test_retrieve_context_with_results(service, monkeypatch):
    mock_vector_service = MagicMock()
    mock_vector_service_instance = AsyncMock()
    mock_vector_service_instance.search.return_value = [("chunk1", 0.9)]
    mock_vector_service.return_value = mock_vector_service_instance
    monkeypatch.setattr("backend.modules.chatbot.chatbot_service.VectorSearchService", mock_vector_service)
    
    mock_chunk = MagicMock()
    mock_chunk.content = "chunk content"
    mock_chunk.start_time = 15.0
    mock_chunk.document_id = "doc1"
    service.chunk_repo.get_by_ids.return_value = [mock_chunk]
    
    context, ts, doc = await service._retrieve_context("doc1", "query")
    assert context == "chunk content"
    assert ts == 15.0
    assert doc == "doc1"

def test_extract_timestamp(service):
    assert service._extract_timestamp("Look at [12.5]") == 12.5
    assert service._extract_timestamp("No timestamp here") is None
    assert service._extract_timestamp("[100]") == 100.0
