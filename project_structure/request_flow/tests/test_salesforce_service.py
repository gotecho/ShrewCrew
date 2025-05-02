import pytest
from unittest.mock import patch
from request_flow.services import salesforce_service

@pytest.fixture
def mock_auth_response():
    return {
        "access_token": "mock_access_token",
        "instance_url": "https://mock.salesforce.com"
    }

def test_create_service_request_success(mock_auth_response):
    with patch("request_flow.services.salesforce_service.authenticate_salesforce", return_value=mock_auth_response), \
         patch("request_flow.services.salesforce_service.requests.post") as mock_post:
        
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "CASE123"}

        result = salesforce_service.create_service_request("Test issue")
        assert result["case_id"] == "CASE123"
        assert result["message"] == "Case created successfully."

def test_create_service_request_failure(mock_auth_response):
    with patch("request_flow.services.salesforce_service.authenticate_salesforce", return_value=mock_auth_response), \
         patch("request_flow.services.salesforce_service.requests.post") as mock_post:

        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"

        result = salesforce_service.create_service_request("Invalid issue")
        assert "error" in result
        assert "Failed to create case" in result["error"]

def test_get_case_status_success(mock_auth_response):
    with patch("request_flow.services.salesforce_service.authenticate_salesforce", return_value=mock_auth_response), \
         patch("request_flow.services.salesforce_service.requests.get") as mock_get:

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "Status": "New",
            "Description": "This is a test case."
        }

        result = salesforce_service.get_case_status("CASE123")
        assert result["status"] == "New"
        assert result["description"] == "This is a test case."

def test_get_case_status_not_found(mock_auth_response):
    with patch("request_flow.services.salesforce_service.authenticate_salesforce", return_value=mock_auth_response), \
         patch("request_flow.services.salesforce_service.requests.get") as mock_get:

        mock_get.return_value.status_code = 404

        result = salesforce_service.get_case_status("CASE404")
        assert "error" in result
        assert result["error"] == "Case not found."

def test_get_case_status_server_error(mock_auth_response):
    with patch("request_flow.services.salesforce_service.authenticate_salesforce", return_value=mock_auth_response), \
         patch("request_flow.services.salesforce_service.requests.get") as mock_get:

        mock_get.return_value.status_code = 500
        mock_get.return_value.text = "Internal Server Error"

        result = salesforce_service.get_case_status("CASE500")
        assert "error" in result
        assert "Error retrieving case" in result["error"]