import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from backend.modules.media.media_service import MediaService
from backend.modules.media.media_models import Transcript, TranscriptSegment
import datetime

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def service(mock_db):
    service = MediaService(db=mock_db)
    service.transcript_repo = MagicMock()
    service.segment_repo = MagicMock()
    return service

@pytest.mark.asyncio
async def test_transcribe_media_success(service, monkeypatch):
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {
        "text": "Full text.",
        "segments": [{"text": "Full text.", "start": 0.0, "end": 1.0}]
    }
    
    mock_whisper = MagicMock()
    mock_whisper.load_model.return_value = mock_model
    monkeypatch.setattr("backend.modules.media.media_service.whisper", mock_whisper)
    
    mock_transcript = Transcript(
        id="t1",
        document_id="doc1",
        full_text="Full text.",
        language="en",
        created_at=datetime.datetime.now()
    )
    service.transcript_repo.create.return_value = mock_transcript
    
    mock_segment = TranscriptSegment(id="s1", content="Full text.", start_time=0.0, end_time=1.0)
    service.segment_repo.create.return_value = mock_segment
    
    res = await service.transcribe_media("dummy.mp4", "doc1")
    
    assert res.id == "t1"
    assert res.duration_seconds == 1
    assert len(res.segments) == 1
    service.transcript_repo.update.assert_called_once_with(mock_transcript)

@pytest.mark.asyncio
async def test_transcribe_media_error(service, monkeypatch):
    mock_whisper = MagicMock()
    mock_whisper.load_model.side_effect = Exception("Whisper error")
    monkeypatch.setattr("backend.modules.media.media_service.whisper", mock_whisper)
    
    with pytest.raises(HTTPException) as excinfo:
        await service.transcribe_media("dummy.mp4", "doc1")
        
    assert excinfo.value.status_code == 500

def test_get_transcript_not_found(service):
    service.transcript_repo.get_by_document.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_transcript("doc1")
    assert excinfo.value.status_code == 404

def test_get_transcript_segments_not_found(service):
    service.transcript_repo.get_by_document.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_transcript_segments("doc1")
    assert excinfo.value.status_code == 404
