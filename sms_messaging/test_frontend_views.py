import pytest
from unittest.mock import patch, MagicMock
from msg_app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("msg_app.firestore")
@patch("msg_app.Client")
def test_sms_page_loads(mock_twilio, mock_firestore, client):
    mock_firestore.client.return_value.collection.return_value.order_by.return_value.limit.return_value.stream.return_value = []
    client.post("/form_login", data={"username": "ShrewCrew", "password": "123Password"}, follow_redirects=True)
    response = client.get("/sms")
    assert response.status_code == 200
    assert b"<table" in response.data

@patch("msg_app.firestore")
@patch("msg_app.Client")
def test_sms_table_rendered(mock_twilio, mock_firestore, client):
    mock_twilio.return_value.messages.list.return_value = [
        MagicMock(
            date_sent="2025-05-02",
            from_="+11234567890",
            to="+10987654321",
            body="This is a test message",
            sid="SM1234567890"
        )
    ]
    client.post("/form_login", data={"username": "ShrewCrew", "password": "123Password"}, follow_redirects=True)
    response = client.get("/sms")
    assert b"<table" in response.data
    assert b"This is a test message" in response.data

@patch("msg_app.firestore")
@patch("msg_app.Client")
def test_sms_page_shows_empty_message(mock_twilio, mock_firestore, client):
    mock_twilio.return_value.messages.list.return_value = []
    client.post("/form_login", data={"username": "ShrewCrew", "password": "123Password"}, follow_redirects=True)
    response = client.get("/sms")
    assert b"No messages available." in response.data

@patch("msg_app.firestore")
@patch("msg_app.Client")
def test_statistics_page_loads(mock_twilio, mock_firestore, client):
    mock_firestore.client.return_value.collection.return_value.stream.return_value = []
    client.post("/form_login", data={"username": "ShrewCrew", "password": "123Password"}, follow_redirects=True)
    response = client.get("/tickets")
    assert response.status_code == 200
    assert b"<table" in response.data or b"No ticket data available." in response.data

@patch("msg_app.firestore")
@patch("msg_app.Client")
def test_statistics_bar_chart_rendered(mock_twilio, mock_firestore, client):
    mock_firestore.client.return_value.collection.return_value.stream.return_value = []
    client.post("/form_login", data={"username": "ShrewCrew", "password": "123Password"}, follow_redirects=True)
    response = client.get("/tickets")
    assert b"<canvas" in response.data

@patch("msg_app.fetch_tickets_from_firestore")
@patch("msg_app.Client")
def test_statistics_table_rendered(mock_twilio, mock_fetch_tickets, client):
    import datetime
    mock_fetch_tickets.return_value = [{
        "case_id": "ABC123",
        "issue_type": "Trash",
        "status": "Open",
        "phone": "1234567890",
        "created_at": datetime.datetime(2025, 5, 2)
    }]
    client.post("/form_login", data={"username": "ShrewCrew", "password": "123Password"}, follow_redirects=True)
    response = client.get("/tickets")
    assert b"<table" in response.data
    assert b"ABC123" in response.data

@patch("msg_app.fetch_tickets_from_firestore")
@patch("msg_app.Client")
def test_statistics_page_shows_empty_message(mock_twilio, mock_fetch_tickets, client):
    mock_fetch_tickets.return_value = []
    
    client.post("/form_login", data={"username": "ShrewCrew", "password": "123Password"}, follow_redirects=True)
    response = client.get("/tickets")

    assert b'colspan="6">No ticket data available.' in response.data