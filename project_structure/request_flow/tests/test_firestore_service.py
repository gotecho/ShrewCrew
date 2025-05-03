import pytest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
import sys


@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        'GOOGLE_PROJECT_ID': 'mock-project-id',
        'GOOGLE_APPLICATION_CREDENTIALS': 'mock-credentials.json',
        'REGION': 'us-central1',
        'GOOGLE_AGENT_ID': 'mock-agent-id',
        'SALESFORCE_USERNAME': 'mock-user',
        'SALESFORCE_PASSWORD': 'mock-password',
        'SALESFORCE_SECURITY_TOKEN': 'mock-token',
        'SALESFORCE_INSTANCE_URL': 'https://mock.salesforce.com',
        'TWILIO_ACCOUNT_SID': 'mock-sid',
        'TWILIO_AUTH_TOKEN': 'mock-auth-token',
        'TWILIO_PHONE_NUMBER': '+15551234567',
        'SECRET_KEY': 'mock-secret',
    }):
        yield

@pytest.fixture
def mock_firestore():
    with patch("project_structure.request_flow.services.firestore_service.get_firestore_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        yield mock_client

def test_get_latest_request_found(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {"case_id": "123", "timestamp": datetime.now(timezone.utc)}
    mock_firestore.collection.return_value.where.return_value.order_by.return_value.limit.return_value.get.return_value = [mock_doc]
    result = firestore_service.get_latest_request("123")
    assert result["case_id"] == "123"

def test_get_latest_request_not_found(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_firestore.collection.return_value.where.return_value.order_by.return_value.limit.return_value.get.return_value = []
    result = firestore_service.get_latest_request("notfound")
    assert result is None

def test_get_latest_request_exception(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_firestore.collection.return_value.where.return_value.order_by.return_value.limit.return_value.get.side_effect = Exception("Firestore failed")
    result = firestore_service.get_latest_request("123")
    assert result is None

def test_save_request(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    firestore_service.save_request({"Body": "pothole", "From": "5551234567"}, "mock-session-id")
    mock_doc.set.assert_called_once()

def test_get_all_cases(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_doc = MagicMock()
    mock_doc.id = "doc1"
    mock_doc.to_dict.return_value = {"case_id": "123"}
    mock_firestore.collection.return_value.stream.return_value = [mock_doc]
    assert firestore_service.get_all_cases() == [{"case_id": "123", "id": "doc1"}]

def test_update_request_status(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    firestore_service.update_request_status("123", "Resolved")
    mock_doc.update.assert_called_with({"status": "Resolved"})

def test_delete_request(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    firestore_service.delete_request("123")
    mock_doc.delete.assert_called_once()

def test_log_message(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_collection = MagicMock()
    mock_firestore.collection.return_value.document.return_value.collection.return_value = mock_collection
    firestore_service.log_message("5551234567", "Hello there")
    mock_collection.add.assert_called_once()

def test_generate_session_id():
    from project_structure.request_flow.services import firestore_service
    result = firestore_service.generate_session_id()
    assert isinstance(result, str)
    assert len(result) == 32
    int(result, 16)  # no exception means it's a valid hex

def test_set_user_session(mock_firestore):
    from project_structure.request_flow.services import firestore_service
    mock_doc = MagicMock()
    mock_firestore.collection.return_value.document.return_value = mock_doc
    firestore_service.set_user_session("5551234567", "session-abc")
    mock_doc.set.assert_called_once()

def test_get_user_session_valid(mock_firestore):
    from project_structure.request_flow.services import firestore_service
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
    from project_structure.request_flow.services import firestore_service
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
    from project_structure.request_flow.services import firestore_service
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = None
    mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
    result = firestore_service.get_user_session("5551234567")
    assert result is None

