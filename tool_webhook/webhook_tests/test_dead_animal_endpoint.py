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
def test_dead_animal_success(mock_geocode, mock_post, mock_get_token, client):
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

    animal_data = {
        "locationType": "Right of Way",
        "location": "123 Main St",
        "animalType": "Dog",
        "animalTotal": "1",
        "chamActivityType": "DEAD ST",
        "chamActivitySubType": "DEAD ST",
        "chamPriority": "4",
        "firstName": "Bob",
        "lastName": "Jones",
        "phoneNumber": "1234567890"
    }

    # Mock response of requests.post to simulate a successful case creation
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"Success": True, "id": "123456"}
    response = client.post('/dead_animal', json=animal_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['Success'] == True
    assert json_data['Case Id'] == '123456'


@patch('dialogflow_tools.playbook_tool_webhook.getToken', return_value='dummy_token')
@patch('dialogflow_tools.playbook_tool_webhook.requests.post')
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_dead_animal_fail(mock_geocode, mock_post, mock_get_token, client):
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

    animal_data = {
        "locationType": "Right of Way",
        "location": "123 Main St",
        "animalType": "Dog",
        "animalTotal": "1",
        "chamActivityType": "DEAD ST",
        "chamActivitySubType": "DEAD ST",
        "chamPriority": "4",
        "firstName": "Bob",
        "lastName": "Jones",
        "phoneNumber": "1234567890"
    }

    mock_post.side_effect = Exception("Internal Server Error Occurred.")

    response = client.post('/dead_animal', json=animal_data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['Success'] == False
    assert 'Error' in json_data
    assert json_data['Error'] == 'Internal Server Error Occurred.'



@patch('dialogflow_tools.playbook_tool_webhook.getToken', return_value='dummy_token')
@patch('dialogflow_tools.playbook_tool_webhook.requests.post')
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_dead_animal_outside_area(mock_geocode, mock_post, mock_get_token, client): 
     mock_geocode.return_value = {
        "internal_geocoder": {}
    }
     animal_data = {
        "locationType": "Right of Way",
        "location": "N/A",
        "animalType": "Dog",
        "animalTotal": "1",
        "chamActivityType": "DEAD ST",
        "chamActivitySubType": "DEAD ST",
        "chamPriority": "4",
        "firstName": "N/A",
        "lastName": "N/A",
        "phoneNumber": "N/A"
    }
     
     mock_post.return_value.status_code = 401
     mock_post.return_value.json.return_value = {"Success": False, "Error": "Address is outside the service area"}

     response = client.post('/dead_animal', json=animal_data)
     assert response.status_code == 401
     json_data = response.get_json()
     assert json_data['Success'] == False
     assert 'Error' in json_data
     assert json_data['Error'] == 'Address is outside the service area'
   
     


