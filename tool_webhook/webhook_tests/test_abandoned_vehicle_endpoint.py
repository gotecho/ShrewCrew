import json
import pytest
from unittest.mock import patch
from dialogflow_tools.playbook_tool_webhook import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Mock the getToken function to return a dummy token
@patch('app.getToken', return_value='dummy_token')
# Mock the requests.post to avoid making actual HTTP requests
@patch('requests.post')
def test_abandoned_vehicle(mock_post, mock_get_token, client):
    vehicle_data = {
        "make": "Test Make",
        "model": "Test Model",
        "vehicleColor": "Test Color",
        "licensePlate": "123 Test",
        "timePeriod": 0,
        "location": "123 Test Drive",
        "firstName": "John",
        "lastName": "Doe",
        "phoneNumber": "123-456-789"
    }

    # Mock response of requests.post to simulate a successful case creation
    mock_post.return_value.json.return_value = {"Success": True, "Case id": "123456"}

    response = client.post('/file-abandoned-vehicle', 
                           data=json.dumps(vehicle_data),
                           content_type='application/json')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['Success'] == True
    assert 'Case Id' in json_data
    assert json_data['Case Id'] == '123456'


@patch('app.getToken', return_value='dummy_token')
@patch('requests.post')
def test_abandoned_vehicle_failure(mock_post, mock_get_token, client):
    vehicle_data = {
        "make": "Test Make",
        "model": "Test Model",
        "vehicleColor": "Test Color",
        "licensePlate": "123 Test",
        "timePeriod": 0,
        "location": "123 Test Drive",
        "firstName": "John",
        "lastName": "Doe",
        "phoneNumber": "123-456-789"
    }

    mock_post.side_effect = Exception("Request failed")

    response = client.post('/file-abandoned-vehicle', 
                           data=json.dumps(vehicle_data),
                           content_type='application/json')

    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['Success'] == False
    assert 'Error' in json_data
    assert json_data['Error'] == 'Request failed'
