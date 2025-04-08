import pytest
from unittest.mock import patch
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dialogflow_tools')))

from dialogflow_tools.playbook_tool_webhook import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

# Successful case
@patch("dialogflow_tools.playbook_tool_webhook.getToken", return_value="mocked_token")
@patch("dialogflow_tools.playbook_tool_webhook.requests.post")
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_successful_case_post(mock_geocode, mock_post, mock_token, client):
    mock_geocode.return_value = {
        "internal_geocoder": {
            "candidates": [{
                "location": {"x": -121.5, "y": 38.5},
                "attributes": {
                    "X": -121.5,
                    "Y": 38.5,
                    "City": "Sacramento",
                    "Loc_name": "StreetCenterLine"
                },
                "address": "123 Main St"
            }]
        }
    }

    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": "500XYZ"}

    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "phone": "1234567890",
        "issueType": "Pothole",
        "description": "There is a pothole on my street",
        "address": "123 Main St, Sacramento, CA"
    }

    response = client.post("/generic-case-post", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "salesforce_response" in data

# Address not found (Failure)
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_address_outside_service_area(mock_geocode, client):
    mock_geocode.return_value = {"internal_geocoder": {}}

    payload = {
        "firstName": "Jane",
        "lastName": "Smith",
        "phone": "1234567890",
        "issueType": "Street Light",
        "description": "Street light is not working",
        "address": "Unknown Address"
    }

    response = client.post("/generic-case-post", json=payload)
    data = response.get_json()
    assert response.status_code == 401
    assert data["success"] is False
    assert "Address is outside the service area" in data["error"]

# Salesforce error (Failure)
@patch("dialogflow_tools.playbook_tool_webhook.getToken", return_value="mocked_token")
@patch("dialogflow_tools.playbook_tool_webhook.requests.post")
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_salesforce_error(mock_geocode, mock_post, mock_token, client):
    mock_geocode.return_value = {
        "internal_geocoder": {
            "candidates": [{
                "location": {"x": -121.5, "y": 38.5},
                "attributes": {
                    "X": -121.5,
                    "Y": 38.5,
                    "City": "Sacramento",
                    "Loc_name": "StreetCenterLine"
                },
                "address": "123 Main St"
            }]
        }
    }

    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"

    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "phone": "1234567890",
        "issueType": "Pothole",
        "description": "There is a pothole on my street",
        "address": "123 Main St, Sacramento, CA"
    }

    response = client.post("/generic-case-post", json=payload)
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False
    assert "Salesforce API returned 400" in data["error"]

# Invalid JSON body (Failure)
def test_invalid_json(client):
    response = client.post("/generic-case-post", data="not-a-json")
    assert response.status_code == 500

# Missing required fields (Failure)
def test_missing_required_fields(client):
    payload = {
        "firstName": "John",
        "description": "Missing fields",
        "address": "123 Main St"
    }

    response = client.post("/generic-case-post", json=payload)
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False
    assert "Missing required fields" in data["error"]

# Invalid phone number (Failure)
def test_invalid_phone_format(client):
    payload = {
        "firstName": "John",
        "lastName": "Doe",
        "phone": "abc123",
        "issueType": "Pothole",
        "description": "Bad phone",
        "address": "123 Main St"
    }

    response = client.post("/generic-case-post", json=payload)
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False
    assert "Invalid phone number" in data["error"]

# Empty candidates list in geocode (Failure)
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_empty_candidates_list(mock_geocode, client):
    mock_geocode.return_value = {
        "internal_geocoder": {
            "candidates": []
        }
    }

    payload = {
        "firstName": "Alex",
        "lastName": "Smith",
        "phone": "1234567890",
        "issueType": "Graffiti",
        "description": "Graffiti on wall",
        "address": "456 Elm St"
    }

    response = client.post("/generic-case-post", json=payload)
    data = response.get_json()
    assert response.status_code == 401
    assert data["success"] is False
    assert "Address is outside the service area" in data["error"]

# Geocoder crashes (Failure)
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode", side_effect=Exception("Geocoder crashed"))
def test_geocoder_crash(mock_geocode, client):
    payload = {
        "firstName": "Crash",
        "lastName": "Dummy",
        "phone": "1234567890",
        "issueType": "Fire",
        "description": "Fire reported",
        "address": "789 Oak St"
    }

    response = client.post("/generic-case-post", json=payload)
    assert response.status_code == 500

# Unexpected field types (Failure)
def test_unexpected_field_types(client):
    payload = {
        "firstName": 123,
        "lastName": "Doe",
        "phone": "1234567890",
        "issueType": "Trash",
        "description": ["This", "is", "a", "list"],
        "address": "Some address"
    }

    response = client.post("/generic-case-post", json=payload)
    assert response.status_code == 400

# Token fetching fails (Failure)
@patch("dialogflow_tools.playbook_tool_webhook.getToken", side_effect=Exception("Auth failed"))
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_token_fetch_fails(mock_geocode, mock_token, client):
    mock_geocode.return_value = {
        "internal_geocoder": {
            "candidates": [{
                "location": {"x": -121.5, "y": 38.5},
                "attributes": {
                    "X": -121.5,
                    "Y": 38.5,
                    "City": "Sacramento",
                    "Loc_name": "StreetCenterLine"
                },
                "address": "123 Main St"
            }]
        }
    }

    payload = {
        "firstName": "Auth",
        "lastName": "Fail",
        "phone": "1234567890",
        "issueType": "Illegal Dumping",
        "description": "Unauthorized trash dump",
        "address": "Somewhere"
    }

    response = client.post("/generic-case-post", json=payload)
    assert response.status_code == 500
