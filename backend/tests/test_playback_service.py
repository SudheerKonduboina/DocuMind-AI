import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from backend.modules.playback.playback_service import PlaybackService
from backend.modules.playback.playback_schemas import PlaybackSegmentRequest
from backend.modules.document.document_models import Document
from backend.modules.media.media_models import Transcript, TranscriptSegment


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    return PlaybackService(db=mock_db)


@pytest.mark.asyncio
async def test_get_playback_segment_success(service, monkeypatch):
    doc_id = "doc1"
    user_id = "user1"
    req = PlaybackSegmentRequest(timestamp=10.0, duration=10.0)

    mock_doc = Document(id=doc_id, s3_key="s3_key_value")
    service.document_repo.get_by_id = MagicMock(return_value=mock_doc)

    mock_transcript = Transcript(id="trans1", duration_seconds=100.0)
    service.transcript_repo.get_by_document = MagicMock(return_value=mock_transcript)

    mock_segments = [
        TranscriptSegment(content="Hello"),
        TranscriptSegment(content="World"),
    ]
    service.segment_repo.get_by_time_range = MagicMock(return_value=mock_segments)

    # Mock S3 service
    mock_s3 = AsyncMock()
    mock_s3.generate_presigned_url.return_value = "https://s3.url"
    monkeypatch.setattr("backend.modules.playback.playback_service.s3_service", mock_s3)

    res = await service.get_playback_segment(doc_id, user_id, req)

    assert res.start_time == 5.0
    assert res.end_time == 15.0
    assert res.transcript == "Hello World"
    assert res.s3_url == "https://s3.url"


@pytest.mark.asyncio
async def test_get_playback_segment_doc_not_found(service):
    doc_id = "doc1"
    user_id = "user1"
    req = PlaybackSegmentRequest(timestamp=10.0, duration=10.0)

    service.document_repo.get_by_id = MagicMock(return_value=None)

    with pytest.raises(HTTPException) as excinfo:
        await service.get_playback_segment(doc_id, user_id, req)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Document not found"


@pytest.mark.asyncio
async def test_get_playback_segment_transcript_not_found(service):
    doc_id = "doc1"
    user_id = "user1"
    req = PlaybackSegmentRequest(timestamp=10.0, duration=10.0)

    mock_doc = Document(id=doc_id, s3_key="s3_key_value")
    service.document_repo.get_by_id = MagicMock(return_value=mock_doc)
    service.transcript_repo.get_by_document = MagicMock(return_value=None)

    with pytest.raises(HTTPException) as excinfo:
        await service.get_playback_segment(doc_id, user_id, req)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Transcript not found for this document"


@pytest.mark.asyncio
async def test_get_playback_segment_no_s3_key(service, monkeypatch):
    doc_id = "doc1"
    user_id = "user1"
    req = PlaybackSegmentRequest(timestamp=10.0, duration=10.0)

    # Document without s3_key
    mock_doc = Document(id=doc_id, s3_key=None)
    service.document_repo.get_by_id = MagicMock(return_value=mock_doc)

    mock_transcript = Transcript(id="trans1", duration_seconds=100.0)
    service.transcript_repo.get_by_document = MagicMock(return_value=mock_transcript)
    service.segment_repo.get_by_time_range = MagicMock(return_value=[])

    res = await service.get_playback_segment(doc_id, user_id, req)

    assert res.s3_url is None


@pytest.mark.asyncio
async def test_get_media_url_success(service, monkeypatch):
    doc_id = "doc1"
    user_id = "user1"

    mock_doc = Document(id=doc_id, s3_key="s3_key_value")
    service.document_repo.get_by_id = MagicMock(return_value=mock_doc)

    mock_s3 = AsyncMock()
    mock_s3.generate_presigned_url.return_value = "https://s3.url"
    monkeypatch.setattr("backend.modules.playback.playback_service.s3_service", mock_s3)

    res = await service.get_media_url(doc_id, user_id)

    assert res == "https://s3.url"


@pytest.mark.asyncio
async def test_get_media_url_doc_not_found(service):
    doc_id = "doc1"
    user_id = "user1"

    service.document_repo.get_by_id = MagicMock(return_value=None)

    with pytest.raises(HTTPException) as excinfo:
        await service.get_media_url(doc_id, user_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Document not found"
