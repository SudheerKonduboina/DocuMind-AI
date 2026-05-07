import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from backend.modules.playback.playback_repository import PlaybackRepository
from backend.modules.playback.playback_models import PlaybackSession


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def repo(mock_db_session):
    return PlaybackRepository(db=mock_db_session)


def test_create_playback_session(repo, mock_db_session):
    user_id = "user1"
    document_id = "doc1"
    start_time = 0.0
    end_time = 10.5

    session = repo.create_playback_session(user_id, document_id, start_time, end_time)

    assert isinstance(session, PlaybackSession)
    assert session.user_id == user_id
    assert session.document_id == document_id
    assert session.start_time == start_time
    assert session.end_time == end_time

    mock_db_session.add.assert_called_once_with(session)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(session)


def test_get_playback_session(repo, mock_db_session):
    session_id = "sess1"
    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value
    expected_session = PlaybackSession(id=session_id)
    mock_filter.first.return_value = expected_session

    result = repo.get_playback_session(session_id)

    assert result == expected_session
    mock_db_session.query.assert_called_once_with(PlaybackSession)


def test_get_user_playback_sessions(repo, mock_db_session):
    user_id = "user1"
    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_order_by = mock_filter.order_by.return_value
    expected_sessions = [PlaybackSession(user_id=user_id)]
    mock_order_by.all.return_value = expected_sessions

    result = repo.get_user_playback_sessions(user_id)

    assert result == expected_sessions
    mock_db_session.query.assert_called_once_with(PlaybackSession)


def test_update_playback_session_success(repo, mock_db_session, monkeypatch):
    session_id = "sess1"
    end_time = 20.0
    existing_session = PlaybackSession(id=session_id, end_time=10.0)

    def mock_get(*args, **kwargs):
        return existing_session

    monkeypatch.setattr(repo, "get_playback_session", mock_get)

    result = repo.update_playback_session(session_id, end_time=end_time)

    assert result == existing_session
    assert existing_session.end_time == end_time
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(existing_session)


def test_update_playback_session_not_found(repo, mock_db_session, monkeypatch):
    session_id = "sess1"

    def mock_get(*args, **kwargs):
        return None

    monkeypatch.setattr(repo, "get_playback_session", mock_get)

    result = repo.update_playback_session(session_id, end_time=20.0)

    assert result is None
    mock_db_session.commit.assert_not_called()


def test_delete_playback_session_success(repo, mock_db_session, monkeypatch):
    session_id = "sess1"
    existing_session = PlaybackSession(id=session_id)

    def mock_get(*args, **kwargs):
        return existing_session

    monkeypatch.setattr(repo, "get_playback_session", mock_get)

    result = repo.delete_playback_session(session_id)

    assert result is True
    mock_db_session.delete.assert_called_once_with(existing_session)
    mock_db_session.commit.assert_called_once()


def test_delete_playback_session_not_found(repo, mock_db_session, monkeypatch):
    session_id = "sess1"

    def mock_get(*args, **kwargs):
        return None

    monkeypatch.setattr(repo, "get_playback_session", mock_get)

    result = repo.delete_playback_session(session_id)

    assert result is False
    mock_db_session.delete.assert_not_called()
