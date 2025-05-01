import json
import pytest
import sys, os
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dialogflow_tools')))
from dialogflow_tools.playbook_tool_webhook import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Sucessful Test
@patch('dialogflow_tools.scraper.scrape_city_data')
def test_311_data_success(mock_scrape, client):
    mock_scrape.return_value = {
        "success": True,
        "results": [
            {"title": "Illegal Dumping - Report", "url": "https://311.sacramento.gov/illegal-dumping"},
            {"title": "How to File a Complaint", "url": "https://311.sacramento.gov/complaints"}
        ]
    }

    response = client.post('/311-data', json={'userQuery': 'How do I report illegal dumping?'})
    assert response.status_code == 200
    json_data = response.get_json()

    assert json_data['success'] == True
    assert 'results' in json_data
    assert isinstance(json_data['results'], list)
    assert len(json_data['results']) == 2
    assert json_data['results'][0]['url'].startswith('https://')

# Missing userQuery
def test_311_data_missing_user_query(client):
    response = client.post('/311-data', json={})  
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['success'] == False
    assert json_data['error'] == "Missing 'userQuery' in the request body"

# Scraper throws an exception
@patch('dialogflow_tools.scraper.scrape_city_data', side_effect=Exception("Scraping service is down"))
def test_311_data_scrape_failure(mock_scrape, client):
    response = client.post('/311-data', json={'userQuery': 'parks'})
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['success'] == False
    assert json_data['error'] == 'Failed to scrape data'
    assert 'details' in json_data
    assert json_data['details'] == 'Scraping service is down'

#Json data is malformed
def test_311_data_malformed_json(client):
    response = client.post('/311-data', data="not a json", content_type='application/json')
    assert response.status_code == 400 or response.status_code == 500  

#User submits an empty query
def test_311_data_empty_string_user_query(client):
    response = client.post('/311-data', json={'userQuery': ''})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['success'] is False
    assert json_data['error'] == "Missing 'userQuery' in the request body"

#User submits a very long query
@patch('dialogflow_tools.scraper.scrape_city_data')
def test_311_data_long_query(mock_scrape, client):
    mock_scrape.return_value = {"success": True, "results": []}
    long_query = "graffiti" * 1000  # very long string

    response = client.post('/311-data', json={'userQuery': long_query})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
