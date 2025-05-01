import pytest

@pytest.fixture(autouse=True)
def mock_twilio_verification(mocker):
    mocker.patch("app.routes.verify_twilio_request")

@pytest.fixture(autouse=True)
def mock_twilio_auth_token(monkeypatch):
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "dummy_token")

@pytest.fixture(autouse=True)
def mock_credentials(mocker):
    mocker.patch(
        "app.dialogflow_cx.service_account.Credentials.from_service_account_file"
    )

# Simulates an end-to-end message cycle to ensure Twilio and Dialogflow work together.
from flask import Flask
from app.routes import main

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(main)
    app.config["TESTING"] = True
    return app.test_client()

def test_sms_reply_integration(mocker, client):
    mocker.patch("app.routes.detect_intent_text", return_value="Test Response")

    response = client.post("/sms", data={"Body": "Hello", "From": "+1234567890"})

    assert response.status_code == 200
    assert "<Response><Message>Test Response</Message></Response>" in response.get_data(as_text=True)


