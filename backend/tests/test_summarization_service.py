import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from backend.modules.summarization.summarization_service import SummarizationService
from backend.modules.summarization.summarization_models import Summary


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

    mock_summary = Summary(id="s1", content="Cached summary", summary_type="auto")
    service.summary_repo.create.return_value = mock_summary

    res = await service.generate_summary("doc1", "user1", summary_type="auto")

    assert res.content == "Cached summary"
    service.summary_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_summary_no_content(service):
    service.cache_service.get.return_value = None

    # Mock no chunks and no transcript
    service.chunk_repo.get_by_document.return_value = []
    service.transcript_repo.get_by_document.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await service.generate_summary("doc1", "user1")

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

    existing_summary = Summary(id="s1")
    service.summary_repo.get_by_document.return_value = existing_summary

    updated_summary = Summary(id="s1", content="Generated summary")
    service.summary_repo.update.return_value = updated_summary

    res = await service.generate_summary("doc1", "user1")

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

    new_summary = Summary(id="s1", content="Generated summary")
    service.summary_repo.create.return_value = new_summary

    res = await service.generate_summary("doc1", "user1")

    assert res.content == "Generated summary"
    service.summary_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_document_content_transcript(service):
    service.chunk_repo.get_by_document.return_value = []

    mock_transcript = MagicMock()
    mock_transcript.full_text = "Transcript content"
    service.transcript_repo.get_by_document.return_value = mock_transcript

    res = await service._get_document_content("doc1")
    assert res == "Transcript content"


def test_get_summary_not_found(service):
    service.summary_repo.get_by_document.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        service.get_summary("doc1", "user1")

    assert excinfo.value.status_code == 404
