import pytest
from unittest.mock import patch, MagicMock
from msg_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client

@patch('msg_app.Client')
def test_login_page_loads(mock_twilio, client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<form' in response.data

@patch('msg_app.Client')
def test_login_invalid_username(mock_twilio, client):
    response = client.post('/', data={'username': 'wronguser', 'password': 'anything'})
    assert b'Invalid Username' in response.data

@patch('msg_app.Client')
def test_login_invalid_password(mock_twilio, client):
    response = client.post('/', data={'username': 'ShrewCrew', 'password': 'wrongpass'})
    assert b'Invalid Password' in response.data

@patch('msg_app.Client')
def test_login_success(mock_twilio, client):
    response = client.post('/', data={'username': 'ShrewCrew', 'password': '123Password'}, follow_redirects=True)
    assert response.status_code == 200
