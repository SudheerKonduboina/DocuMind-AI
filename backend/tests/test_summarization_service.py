import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from backend.modules.summarization.summarization_service import SummarizationService
from backend.modules.summarization.summarization_models import Summary
from datetime import datetime
import uuid


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    service = SummarizationService(db=mock_db)
    service.summary_repo = MagicMock()
    service.chunk_repo = MagicMock()
    service.transcript_repo = MagicMock()
    service.cache_service = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_generate_summary_cached_auto(service):
    service.cache_service.get.return_value = "Cached summary"

    now = datetime.now()
    s_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    mock_summary = MagicMock(spec=Summary)
    mock_summary.id = s_id
    mock_summary.document_id = doc_id
    mock_summary.user_id = user_id
    mock_summary.content = "Cached summary"
    mock_summary.summary_type = "auto"
    mock_summary.created_at = now
    mock_summary.updated_at = now

    service.summary_repo.create.return_value = mock_summary

    res = await service.generate_summary(doc_id, user_id, summary_type="auto")

    assert res.content == "Cached summary"
    service.summary_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_summary_no_content(service):
    service.cache_service.get.return_value = None

    # Mock no chunks and no transcript
    service.chunk_repo.get_by_document.return_value = []
    service.transcript_repo.get_by_document.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await service.generate_summary(str(uuid.uuid4()), str(uuid.uuid4()))

    assert excinfo.value.status_code == 400
    assert "No content available" in excinfo.value.detail


@pytest.mark.asyncio
async def test_generate_summary_success_existing(service, monkeypatch):
    service.cache_service.get.return_value = None

    mock_chunk = MagicMock()
    mock_chunk.content = "Chunk content"
    service.chunk_repo.get_by_document.return_value = [mock_chunk]

    mock_openai = AsyncMock()
    mock_openai.summarize_text.return_value = "Generated summary"
    monkeypatch.setattr(
        "backend.modules.summarization.summarization_service.openai_service",
        mock_openai,
    )

    now = datetime.now()
    s_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    existing_summary = MagicMock(spec=Summary)
    existing_summary.id = s_id
    existing_summary.document_id = doc_id
    existing_summary.user_id = user_id
    existing_summary.content = "Old"
    existing_summary.summary_type = "auto"
    existing_summary.created_at = now
    existing_summary.updated_at = now

    service.summary_repo.get_by_document.return_value = existing_summary

    updated_summary = MagicMock(spec=Summary)
    updated_summary.id = s_id
    updated_summary.document_id = doc_id
    updated_summary.user_id = user_id
    updated_summary.content = "Generated summary"
    updated_summary.summary_type = "auto"
    updated_summary.created_at = now
    updated_summary.updated_at = now

    service.summary_repo.update.return_value = updated_summary

    res = await service.generate_summary(doc_id, user_id)

    assert res.content == "Generated summary"
    service.summary_repo.update.assert_called_once()
    service.cache_service.set.assert_called_once()


@pytest.mark.asyncio
async def test_generate_summary_success_new(service, monkeypatch):
    service.cache_service.get.return_value = None

    mock_chunk = MagicMock()
    mock_chunk.content = "Chunk content"
    service.chunk_repo.get_by_document.return_value = [mock_chunk]

    mock_openai = AsyncMock()
    mock_openai.summarize_text.return_value = "Generated summary"
    monkeypatch.setattr(
        "backend.modules.summarization.summarization_service.openai_service",
        mock_openai,
    )

    service.summary_repo.get_by_document.return_value = None

    now = datetime.now()
    s_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    new_summary = MagicMock(spec=Summary)
    new_summary.id = s_id
    new_summary.document_id = doc_id
    new_summary.user_id = user_id
    new_summary.content = "Generated summary"
    new_summary.summary_type = "auto"
    new_summary.created_at = now
    new_summary.updated_at = now

    service.summary_repo.create.return_value = new_summary

    res = await service.generate_summary(doc_id, user_id)

    assert res.content == "Generated summary"
    service.summary_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_document_content_transcript(service):
    service.chunk_repo.get_by_document.return_value = []

    mock_transcript = MagicMock()
    mock_transcript.full_text = "Transcript content"
    service.transcript_repo.get_by_document.return_value = mock_transcript

    res = await service._get_document_content(str(uuid.uuid4()))
    assert res == "Transcript content"


def test_get_summary_not_found(service):
    service.summary_repo.get_by_document.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        service.get_summary(str(uuid.uuid4()), str(uuid.uuid4()))

    assert excinfo.value.status_code == 404
