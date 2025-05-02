import pytest
from unittest.mock import patch

from dialogflow_tools.playbook_tool_webhook import app

@pytest.fixture
def payload_base():
    return {
        "firstName": "John",
        "lastName": "Doe",
        "phone": "1234567890",
        "issueType": "Pothole",
        "description": "There is a pothole on my street",
        "address": "123 Main St, Sacramento, CA"
    }

@patch("dialogflow_tools.playbook_tool_webhook.requests.post")
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_successful_case_post(mock_geocode, mock_post, client, payload_base):
    mock_geocode.return_value = {
        "internal_geocoder": {
            "candidates": [{
                "location": {"x": -121.5, "y": 38.5},
                "attributes": {
                    "X": -121.5, "Y": 38.5,
                    "City": "Sacramento", "Loc_name": "StreetCenterLine"
                },
                "address": "123 Main St"
            }]
        }
    }

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"success": True, "salesforce_response": "500WL00000E3K3lYAF"}

    response = client.post("/generic-case-post", json=payload_base)
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "salesforce_response" in data


@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_address_outside_service_area(mock_geocode, client, payload_base):
    mock_geocode.return_value = {"internal_geocoder": {}}
    payload_base["address"] = "Unknown Address"

    response = client.post("/generic-case-post", json=payload_base)
    data = response.get_json()
    assert response.status_code == 401
    assert not data["success"]
    assert "Address is outside the service area" in data["error"]


@patch("dialogflow_tools.playbook_tool_webhook.requests.post")
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_salesforce_error(mock_geocode, mock_post, client, payload_base):
    mock_geocode.return_value = {
        "internal_geocoder": {
            "candidates": [{
                "location": {"x": -121.5, "y": 38.5},
                "attributes": {
                    "X": -121.5, "Y": 38.5,
                    "City": "Sacramento", "Loc_name": "StreetCenterLine"
                },
                "address": "123 Main St"
            }]
        }
    }
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"
    mock_post.return_value.json.return_value = {"success": False, "error": "Salesforce returned with 400"}

    response = client.post("/generic-case-post", json=payload_base)
    data = response.get_json()
    assert response.status_code == 400
    assert not data["success"]
    assert "Salesforce API returned 400" in data["error"]


def test_invalid_json(client):
    response = client.post("/generic-case-post", data="not-a-json")
    assert response.status_code == 500


def test_missing_required_fields(client):
    response = client.post("/generic-case-post", json={"firstName": "John"})
    data = response.get_json()
    assert response.status_code == 400
    assert not data["success"]
    assert "Missing required fields" in data["error"]


def test_invalid_phone_format(client, payload_base):
    payload_base["phone"] = "abc123"
    response = client.post("/generic-case-post", json=payload_base)
    data = response.get_json()
    assert response.status_code == 400
    assert not data["success"]
    assert "Invalid phone number" in data["error"]


@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_empty_candidates_list(mock_geocode, client, payload_base):
    mock_geocode.return_value = {"internal_geocoder": {"candidates": []}}
    response = client.post("/generic-case-post", json=payload_base)
    data = response.get_json()
    assert response.status_code == 401
    assert not data["success"]


@patch("dialogflow_tools.playbook_tool_webhook.a.geocode", side_effect=Exception("Geocoder crashed"))
def test_geocoder_crash(mock_geocode, client, payload_base):
    response = client.post("/generic-case-post", json=payload_base)
    assert response.status_code == 500


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


@patch("dialogflow_tools.playbook_tool_webhook.getToken", side_effect=Exception("Auth failed"))
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_token_fetch_fails(mock_geocode, mock_token, client, payload_base):
    mock_geocode.return_value = {
        "internal_geocoder": {
            "candidates": [{
                "location": {"x": -121.5, "y": 38.5},
                "attributes": {"X": -121.5, "Y": 38.5, "City": "Sacramento", "Loc_name": "StreetCenterLine"},
                "address": "123 Main St"
            }]
        }
    }

    response = client.post("/generic-case-post", json=payload_base)
    assert response.status_code == 500