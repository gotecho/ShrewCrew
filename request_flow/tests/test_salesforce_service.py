import pytest
from unittest.mock import patch, MagicMock
from request_flow.services.salesforce_service import (
    create_service_request_sf,
    get_case_status_sf
)

# Mocks SalesForce API connection, and prevents actual API calls
@pytest.fixture
def mock_salesforce():
    with patch("request_flow.services.salesforce_service.sf") as mock_sf:
        yield mock_sf

# Test: Create a New Salesforce Case
# Ensures correct parameters are passed
def test_create_service_request_sf(mock_salesforce):
    mock_salesforce.Case.create.return_value = {"id": "123ABC"}

    case_id = create_service_request_sf("Streetlight outage")

    assert case_id == "123ABC"
    mock_salesforce.Case.create.assert_called_once_with({
        "Subject": "New 311 Service Request",
        "Description": "Streetlight outage",
        "Status": "New"
    })

# Test: Get Existing Salesforce Case Status
# Checks to make sure that the correct case status is returned
def test_get_case_status_sf(mock_salesforce):
    mock_salesforce.Case.get.return_value = {
        "Status": "Open",
        "Description": "Streetlight outage reported."
    }

    result = get_case_status_sf("123ABC")

    assert result is not None
    assert result["status"] == "Open"
    assert result["description"] == "Streetlight outage reported."
    mock_salesforce.Case.get.assert_called_once_with("123ABC")

# Test: Handle Case Retrieval Error
# Mocks API failure
# Ensures that the function returns "None" and doesn't crash
def test_get_case_status_sf_error(mock_salesforce):
    mock_salesforce.Case.get.side_effect = Exception("Salesforce API error")

    result = get_case_status_sf("999XYZ")

    assert result is None