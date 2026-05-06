import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, UploadFile
from backend.modules.document.document_controller import DocumentController
from backend.config.settings import settings

@pytest.fixture
def controller():
    return DocumentController()

@pytest.mark.asyncio
async def test_upload_document_file_too_large(controller, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 10)
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read.return_value = b"12345678901"
    
    with pytest.raises(HTTPException) as excinfo:
        await controller.upload_document(file=mock_file, title="title", user_id="user1", db=MagicMock())
        
    assert excinfo.value.status_code == 413
    assert "File size exceeds maximum allowed size" in excinfo.value.detail

@pytest.mark.asyncio
async def test_upload_document_invalid_type(controller, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1000)
    monkeypatch.setattr(settings, "ALLOWED_FILE_TYPES", ["pdf"])
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read.return_value = b"123"
    mock_file.filename = "test.txt"
    
    with pytest.raises(HTTPException) as excinfo:
        await controller.upload_document(file=mock_file, title="title", user_id="user1", db=MagicMock())
        
    assert excinfo.value.status_code == 400
    assert "File type not allowed" in excinfo.value.detail

@pytest.mark.asyncio
async def test_upload_document_success_audio(controller, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1000)
    monkeypatch.setattr(settings, "ALLOWED_FILE_TYPES", ["mp3"])
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read.return_value = b"123"
    mock_file.filename = "test.mp3"
    
    mock_service_instance = AsyncMock()
    mock_service_instance.upload_document.return_value = {"id": "doc1"}
    
    mock_service_cls = MagicMock(return_value=mock_service_instance)
    monkeypatch.setattr("backend.modules.document.document_controller.DocumentService", mock_service_cls)
    
    res = await controller.upload_document(file=mock_file, title="title", user_id="user1", db=MagicMock())
    assert res == {"id": "doc1"}
    mock_service_instance.upload_document.assert_called_once()

@pytest.mark.asyncio
async def test_upload_document_success_video(controller, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1000)
    monkeypatch.setattr(settings, "ALLOWED_FILE_TYPES", ["mp4"])
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read.return_value = b"123"
    mock_file.filename = "test.mp4"
    
    mock_service_instance = AsyncMock()
    mock_service_instance.upload_document.return_value = {"id": "doc1"}
    
    mock_service_cls = MagicMock(return_value=mock_service_instance)
    monkeypatch.setattr("backend.modules.document.document_controller.DocumentService", mock_service_cls)
    
    res = await controller.upload_document(file=mock_file, title="title", user_id="user1", db=MagicMock())
    assert res == {"id": "doc1"}

@pytest.mark.asyncio
async def test_upload_document_success_other(controller, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1000)
    monkeypatch.setattr(settings, "ALLOWED_FILE_TYPES", ["unknown"])
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read.return_value = b"123"
    mock_file.filename = "test.unknown"
    
    mock_service_instance = AsyncMock()
    mock_service_instance.upload_document.return_value = {"id": "doc1"}
    
    mock_service_cls = MagicMock(return_value=mock_service_instance)
    monkeypatch.setattr("backend.modules.document.document_controller.DocumentService", mock_service_cls)
    
    res = await controller.upload_document(file=mock_file, title="title", user_id="user1", db=MagicMock())
    assert res == {"id": "doc1"}

@pytest.mark.asyncio
async def test_upload_document_service_error(controller, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1000)
    monkeypatch.setattr(settings, "ALLOWED_FILE_TYPES", ["pdf"])
    
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.read.return_value = b"123"
    mock_file.filename = "test.pdf"
    
    mock_service_instance = AsyncMock()
    mock_service_instance.upload_document.side_effect = Exception("Service error")
    
    mock_service_cls = MagicMock(return_value=mock_service_instance)
    monkeypatch.setattr("backend.modules.document.document_controller.DocumentService", mock_service_cls)
    
    with pytest.raises(HTTPException) as excinfo:
        await controller.upload_document(file=mock_file, title="title", user_id="user1", db=MagicMock())
        
    assert excinfo.value.status_code == 500
    assert "Failed to upload document: Service error" in excinfo.value.detail
