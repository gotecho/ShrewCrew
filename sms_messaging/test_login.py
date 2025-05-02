import pytest
from msg_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<form' in response.data  # Basic check that a form exists

def test_login_invalid_username(client):
    response = client.post('/', data={'username': 'wronguser', 'password': 'anything'})
    assert b'Invalid Username' in response.data

def test_login_invalid_password(client):
    response = client.post('/', data={'username': 'ShrewCrew', 'password': 'wrongpass'})
    assert b'Invalid Password' in response.data

def test_login_success(client):
    response = client.post('/', data={'username': 'ShrewCrew', 'password': '123Password'}, follow_redirects=True)
    response.status_code == 200  
