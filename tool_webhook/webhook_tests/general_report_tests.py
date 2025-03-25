import pytest
from unittest.mock import patch
from dialogflow_tools.playbook_tool_webhook import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

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

def test_invalid_json(client):
    response = client.post("/generic-case-post", data="not-a-json")
    assert response.status_code == 500
