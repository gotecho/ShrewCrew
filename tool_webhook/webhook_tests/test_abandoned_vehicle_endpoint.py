import json
import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dialogflow_tools')))
from unittest.mock import patch
from dialogflow_tools.playbook_tool_webhook import app 


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Mock the getToken function to return a dummy token
@patch('dialogflow_tools.playbook_tool_webhook.getToken', return_value='dummy_token')
# Mock the requests.post to avoid making actual HTTP requests
@patch('dialogflow_tools.playbook_tool_webhook.requests.post')
# Mock a.geocode 
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_success(mock_geocode, mock_post, mock_get_token, client):

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
    
    vehicle_data = {
        "make": "Test Make",
        "model": "Test Model", 
        "vehicleColor": "Cyan",
        "licensePlate": "123ABCD",
        "timePeriod": "2",
        "location": "123 Main St",
        "firstName": "John",
        "lastName": "Doe",
        "phoneNumber": "123-456-7890"
    }

    # Mock response of requests.post to simulate a successful case creation
    mock_post.return_value.status_code = 200 
    mock_post.return_value.json.return_value = {"Success": True, "id": "123456"}
   

    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['Success'] == True
    assert 'Case Id' in json_data
    assert json_data['Case Id'] == '123456'


@patch('dialogflow_tools.playbook_tool_webhook.getToken', return_value='dummy_token')
@patch('dialogflow_tools.playbook_tool_webhook.requests.post')
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_failure(mock_geocode, mock_post, mock_get_token, client):

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

    vehicle_data = {
        "make": "Test Make",
        "model": "Test Model", 
        "vehicleColor": "Cyan",
        "licensePlate": "123ABCD",
        "timePeriod": "2",
        "location": "123 Main St",
        "firstName": "John",
        "lastName": "Doe",
        "phoneNumber": "123-456-7890"
    }

    mock_post.side_effect = Exception("Internal Server Error Occured")
    
    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['Success'] == False
    assert 'Error' in json_data
    assert json_data['Error'] == 'Internal Server Error Occured'


@patch('dialogflow_tools.playbook_tool_webhook.getToken', return_value='dummy_token')
@patch('dialogflow_tools.playbook_tool_webhook.requests.post')
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_outside_area(mock_geocode, mock_post, mock_get_token, client):

    mock_geocode.return_value = {
        "internal_geocoder": {}
    }

    vehicle_data = {
        "make": "Test Make",
        "model": "Test Model", 
        "vehicleColor": "Cyan",
        "licensePlate": "123ABCD",
        "timePeriod": "2",
        "location": "N/A",
        "firstName": "N/A",
        "lastName": "N/A",
        "phoneNumber": "N/A"
    }

    mock_post.return_value.status_code = 401
    mock_post.return_value.json.return_value = {"Success": False, "Error": "Address is outside the service area"}
    
    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['Success'] == False
    assert 'Error' in json_data
    assert json_data['Error'] == 'Address is outside the service area'