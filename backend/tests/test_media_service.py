import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from backend.modules.media.media_service import MediaService
from backend.modules.media.media_models import Transcript, TranscriptSegment
from datetime import datetime
import uuid


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
        "segments": [{"text": "Full text.", "start": 0.0, "end": 1.0}],
    }

    mock_whisper = MagicMock()
    mock_whisper.load_model.return_value = mock_model
    monkeypatch.setattr("backend.modules.media.media_service.whisper", mock_whisper)

    now = datetime.now()
    t_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())

    mock_transcript = MagicMock(spec=Transcript)
    mock_transcript.id = t_id
    mock_transcript.document_id = doc_id
    mock_transcript.full_text = "Full text."
    mock_transcript.language = "en"
    mock_transcript.duration_seconds = 1
    mock_transcript.created_at = now
    mock_transcript.updated_at = now

    service.transcript_repo.create.return_value = mock_transcript

    mock_segment = MagicMock(spec=TranscriptSegment)
    mock_segment.id = str(uuid.uuid4())
    mock_segment.transcript_id = t_id
    mock_segment.content = "Full text."
    mock_segment.start_time = 0.0
    mock_segment.end_time = 1.0
    mock_segment.created_at = now

    service.segment_repo.create.return_value = mock_segment

    res = await service.transcribe_media("dummy.mp4", doc_id)

    assert str(res.id) == t_id
    service.transcript_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_transcribe_media_error(service, monkeypatch):
    mock_whisper = MagicMock()
    mock_whisper.load_model.side_effect = Exception("Whisper error")
    monkeypatch.setattr("backend.modules.media.media_service.whisper", mock_whisper)

    with pytest.raises(HTTPException) as excinfo:
        await service.transcribe_media("dummy.mp4", str(uuid.uuid4()))

    assert excinfo.value.status_code == 500


def test_get_transcript_not_found(service):
    service.transcript_repo.get_by_document.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_transcript(str(uuid.uuid4()))
    assert excinfo.value.status_code == 404


def test_get_transcript_segments_not_found(service):
    service.transcript_repo.get_by_document.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_transcript_segments(str(uuid.uuid4()))
    assert excinfo.value.status_code == 404
