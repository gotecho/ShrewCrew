import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

import request_flow.services.firestore_service as firestore_service


@pytest.fixture
def mock_firestore():
    with patch("request_flow.services.firestore_service.database") as mock_db:
        yield mock_db


def test_get_latest_request_found(mock_firestore):
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {"case_id": "123", "timestamp": datetime.now(timezone.utc)}
    mock_firestore.collection.return_value.where.return_value.order_by.return_value.limit.return_value.get.return_value = [mock_doc]

    result = firestore_service.get_latest_request("123")
    assert result["case_id"] == "123"


def test_get_latest_request_not_found(mock_firestore):
    mock_firestore.collection.return_value.where.return_value.order_by.return_value.limit.return_value.get.return_value = []
    result = firestore_service.get_latest_request("notfound")
    assert result is None


def test_get_latest_request_exception(mock_firestore):
    mock_firestore.collection.return_value.where.return_value.order_by.return_value.limit.return_value.get.side_effect = Exception("Firestore failed")
    result = firestore_service.get_latest_request("123")
    assert result is None


def test_save_request(mock_firestore):
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    request_data = {
        "Body": "pothole",
        "From": "5551234567"
    }
    session_id = "mock-session-id"
    firestore_service.save_request(request_data, session_id)
    mock_doc.set.assert_called_once()


def test_get_all_cases(mock_firestore):
    mock_doc = MagicMock()
    mock_doc.id = "doc1"
    mock_doc.to_dict.return_value = {"case_id": "123"}
    mock_firestore.collection.return_value.stream.return_value = [mock_doc]

    cases = firestore_service.get_all_cases()
    assert cases == [{"case_id": "123", "id": "doc1"}]


def test_update_request_status(mock_firestore):
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    firestore_service.update_request_status("123", "Resolved")
    mock_doc.update.assert_called_with({"status": "Resolved"})


def test_delete_request(mock_firestore):
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    firestore_service.delete_request("123")
    mock_doc.delete.assert_called_once()


def test_log_message(mock_firestore):
    mock_collection = MagicMock()
    mock_firestore.collection.return_value.document.return_value.collection.return_value = mock_collection
    firestore_service.log_message("5551234567", "Hello there")
    mock_collection.add.assert_called_once()


def test_generate_session_id():
    result = firestore_service.generate_session_id()
    assert isinstance(result, str)
    assert len(result) == 32
    int(result, 16)


def test_set_user_session(mock_firestore):
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    firestore_service.set_user_session("5551234567", "session-abc")
    mock_doc.set.assert_called_once()


def test_get_user_session_valid(mock_firestore):
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "session_id": "session-abc",
        "timestamp": datetime.now(timezone.utc)
    }
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    result = firestore_service.get_user_session("5551234567")
    assert result == "session-abc"


def test_get_user_session_expired(mock_firestore):
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "session_id": "session-abc",
        "timestamp": datetime.now(timezone.utc) - timedelta(minutes=31)
    }
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    result = firestore_service.get_user_session("5551234567")
    assert result is None


def test_get_user_session_none_dict(mock_firestore):
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = None
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    result = firestore_service.get_user_session("5551234567")
    assert result is None