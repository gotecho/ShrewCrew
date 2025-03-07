#Uses mock Dialogflow CX response to test Twilio response formatting. /sms route returns 400 if no message body sent
import pytest
from flask import Flask
from app.routes import main

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(main)
    app.config["TESTING"] = True
    return app.test_client()

def test_sms_reply_no_body(client):
    response = client.post("/sms", data={"From": "+1234567890"})
    assert response.status_code == 400
    assert "No message received" in response.get_json()["error"]

def test_sms_reply_mocked_dialogflow(mocker, client):
    mocker.patch("app.dialogflow_cx.detect_intent_text", return_value="Mocked Response")

    response = client.post("/sms", data={"Body": "Hello", "From": "+1234567890"})
    
    assert response.status_code == 200
    assert "Mocked Response" in response.get_data(as_text=True)

def test_sms_reply_dialogflow_failure(mocker, client):
    mocker.patch("app.dialogflow_cx.detect_intent_text", side_effect=Exception("API Error"))

    response = client.post("/sms", data={"Body": "Hello", "From": "+1234567890"})

    assert response.status_code == 200  # Twilio must still return a valid XML response
    assert "No response from Dialogflow." in response.get_data(as_text=True)
