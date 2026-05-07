import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from backend.core.dependencies import (
    get_current_user_id,
    get_optional_user_id,
    get_settings,
)


@pytest.mark.asyncio
async def test_get_current_user_id_success(monkeypatch):

    def mock_decode(token):
        return {"sub": "user123"}

    monkeypatch.setattr("backend.core.dependencies.decode_access_token", mock_decode)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid_token"
    )
    user_id = await get_current_user_id(credentials)
    assert user_id == "user123"


@pytest.mark.asyncio
async def test_get_current_user_id_no_sub(monkeypatch):

    def mock_decode(token):
        return {"other": "value"}  # missing "sub"

    monkeypatch.setattr("backend.core.dependencies.decode_access_token", mock_decode)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid_token"
    )
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user_id(credentials)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_id_invalid_token(monkeypatch):

    def mock_decode(token):
        return None

    monkeypatch.setattr("backend.core.dependencies.decode_access_token", mock_decode)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="invalid_token"
    )
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user_id(credentials)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_optional_user_id_success(monkeypatch):

    def mock_decode(token):
        return {"sub": "user123"}

    monkeypatch.setattr("backend.core.dependencies.decode_access_token", mock_decode)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid_token"
    )
    user_id = await get_optional_user_id(credentials)
    assert user_id == "user123"


@pytest.mark.asyncio
async def test_get_optional_user_id_no_credentials():

    user_id = await get_optional_user_id(None)
    assert user_id is None


@pytest.mark.asyncio
async def test_get_optional_user_id_invalid_token(monkeypatch):

    def mock_decode(token):
        return None

    monkeypatch.setattr("backend.core.dependencies.decode_access_token", mock_decode)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="invalid_token"
    )
    user_id = await get_optional_user_id(credentials)
    assert user_id is None


def test_get_settings():
    settings = get_settings()
    assert settings is not None
