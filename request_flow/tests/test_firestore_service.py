import pytest
import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from request_flow.services.firestore_service import (
    get_latest_request_by_case_id,
    save_request_by_case_id,
    update_request_status,
    delete_request
)

# Mocking Firestore -- replace actual Firestore db with mock version
@pytest.fixture
def mock_firestore():
    with patch("app.services.firestore_service.database") as mock_db:
        yield mock_db


# Test: Get Latest Request
# Checks that correct data is returned
def test_get_latest_request_by_case_id(mock_firestore: MagicMock | AsyncMock):
    mock_collection = mock_firestore.collection.return_value
    mock_query = mock_collection.where.return_value.order_by.return_value.limit.return_value.get

    # Simulated Firestore response
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {
        "case_id": "123456",
        "issue_description": "Pothole on Main St",
        "timestamp": datetime.datetime.utcnow()
    }
    mock_query.return_value = [mock_doc]

    result = get_latest_request_by_case_id("123456")
    assert result is not None
    assert result["case_id"] == "123456"
    assert result["issue_description"] == "Pothole on Main St"


# Test: Save Request
def test_save_request_by_case_id(mock_firestore: MagicMock | AsyncMock):
    mock_collection = mock_firestore.collection.return_value
    mock_document = mock_collection.document.return_value

    save_request_by_case_id("789101", "Streetlight outage")
    
    mock_document.set.assert_called_once()


# Test: Update Request Status
def test_update_request_status(mock_firestore: MagicMock | AsyncMock):
    mock_collection = mock_firestore.collection.return_value
    mock_document = mock_collection.document.return_value

    update_request_status("123456", "Resolved")
    
    mock_document.update.assert_called_once_with({"status": "Resolved"})


# Test: Delete Request
def test_delete_request(mock_firestore: MagicMock | AsyncMock):
    mock_collection = mock_firestore.collection.return_value
    mock_document = mock_collection.document.return_value

    delete_request("123456")
    
    mock_document.delete.assert_called_once()