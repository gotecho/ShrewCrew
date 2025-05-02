import json
import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dialogflow_tools')))
from unittest.mock import patch, MagicMock
from dialogflow_tools.playbook_tool_webhook import app 


# Removed getToken and requests.post patches to rely on conftest.py patches
@patch("dialogflow_tools.playbook_tool_webhook.requests.post")
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_success(mock_geocode, mock_post, client):

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
    # requests.post is patched globally in conftest.py so here we just use it directly
    mock_post.return_value.status_code = 200 
    mock_post.return_value.json.return_value = {"success": True, "id": "123456"}
   

    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] == True
    assert 'caseId' in json_data
    assert json_data['caseId'] == '123456'


@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_failure(mock_geocode, client):

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

    from dialogflow_tools.playbook_tool_webhook import requests
    requests.post.side_effect = Exception("Internal Server Error Occured")
    
    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['success'] == False
    assert 'error' in json_data
    assert json_data['error'] == 'Internal Server Error Occured'


@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_outside_area(mock_geocode, client):

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
        "phoneNumber": "0"
    }

    from dialogflow_tools.playbook_tool_webhook import requests
    requests.post.return_value.status_code = 401
    requests.post.return_value.json.return_value = {"success": False, "error": "Address is outside the service area"}
    
    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['success'] == False
    assert 'error' in json_data
    assert json_data['error'] == 'Address is outside the service area'


@patch("dialogflow_tools.playbook_tool_webhook.requests.post")
@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_salesforce_error(mock_geocode, mock_post, client):

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
        "location": "N/A",
        "firstName": "N/A",
        "lastName": "N/A",
        "phoneNumber": "0"
    }

    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"success": False, "error": "Salesforce returned with 400"}
    
    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['success'] == False
    assert 'error' in json_data
    assert json_data['error'] == 'Salesforce returned with 400'



@patch("dialogflow_tools.playbook_tool_webhook.a.geocode")
def test_abandoned_vehicle_token_error(mock_geocode, client):

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
        "location": "N/A",
        "firstName": "N/A",
        "lastName": "N/A",
        "phoneNumber": "0"
    }

    # Simulate getToken raising Exception by patching in conftest.py, so here just run test
    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 500



@patch("dialogflow_tools.playbook_tool_webhook.a.geocode", side_effect = Exception("Geocode crashed"))
def test_abandoned_vehicle_geocode_error(mock_geocode, client):

    vehicle_data = {
        "make": "Test Make",
        "model": "Test Model", 
        "vehicleColor": "Cyan",
        "licensePlate": "123ABCD",
        "timePeriod": "2",
        "location": "N/A",
        "firstName": "N/A",
        "lastName": "N/A",
        "phoneNumber": "0"
    }

  
    response = client.post('/file-abandoned-vehicle', json=vehicle_data)
    assert response.status_code == 500