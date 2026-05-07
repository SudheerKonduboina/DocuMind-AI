import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from fastapi import HTTPException
from backend.modules.document.document_service import DocumentService
from backend.modules.document.document_models import Document
from datetime import datetime
import os
import uuid


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    service = DocumentService(db=mock_db)
    service.document_repo = MagicMock()
    service.chunk_repo = MagicMock()
    return service


@pytest.mark.asyncio
async def test_upload_document_success(service, monkeypatch):
    mock_s3 = AsyncMock()
    monkeypatch.setattr("backend.modules.document.document_service.s3_service", mock_s3)

    now = datetime.now()
    doc_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.title = "test.pdf"
    mock_doc.file_type = "pdf"
    mock_doc.s3_key = f"{user_id}/test.pdf"
    mock_doc.file_size = 1000
    mock_doc.status = "processing"
    mock_doc.user_id = user_id
    mock_doc.created_at = now
    mock_doc.updated_at = now
    
    service.document_repo.create.return_value = mock_doc

    # Mock _process_pdf
    service._process_pdf = AsyncMock()

    # Mock os.remove
    monkeypatch.setattr(os, "remove", MagicMock())

    res = await service.upload_document(
        file_path="dummy/path.pdf",
        filename="test.pdf",
        file_size=1000,
        file_type="pdf",
        user_id=user_id,
    )

    assert str(res.id) == doc_id
    mock_s3.upload_file.assert_called_once_with("dummy/path.pdf", f"{user_id}/test.pdf")
    service._process_pdf.assert_called_once_with(doc_id, "dummy/path.pdf")


@pytest.mark.asyncio
async def test_process_pdf(service, monkeypatch):
    service._extract_pdf_text = MagicMock(return_value="text")
    service._chunk_text = MagicMock(return_value=["chunk1", "chunk2"])

    await service._process_pdf(str(uuid.uuid4()), "dummy.pdf")

    service.chunk_repo.create_batch.assert_called_once()
    assert len(service.chunk_repo.create_batch.call_args[0][0]) == 2
    service.document_repo.update_status.assert_called_once()


def test_extract_pdf_text(service, monkeypatch):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "page text"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page, mock_page]

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader
    monkeypatch.setattr("backend.modules.document.document_service.pypdf", mock_pypdf)

    m = mock_open(read_data=b"pdf data")
    with patch("builtins.open", m):
        res = service._extract_pdf_text("dummy.pdf")

    assert res == "page text\npage text"


def test_chunk_text(service):
    text = "abcdefghij"
    chunks = service._chunk_text(text, chunk_size=4, overlap=2)
    assert chunks == ["abcd", "cdef", "efgh", "ghij", "ij"]


def test_get_document_not_found(service):
    service.document_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_document(str(uuid.uuid4()), str(uuid.uuid4()))
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_not_found(service):
    service.document_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await service.delete_document(str(uuid.uuid4()), str(uuid.uuid4()))
    assert excinfo.value.status_code == 404


def test_get_document_chunks_not_found(service):
    service.document_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        service.get_document_chunks(str(uuid.uuid4()), str(uuid.uuid4()))
    assert excinfo.value.status_code == 404
