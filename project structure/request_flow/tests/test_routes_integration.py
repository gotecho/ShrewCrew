import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app import create_app

def test_sms_reply_route():
    app = create_app()
    client = app.test_client()

    response = client.post('/sms', data={'Body': 'Test', 'From': '+1234567890'})
    
    assert response.status_code == 200
    # Twilio response
    assert b"<Response>" in response.data  

# NEED TO ADD ROLE -> DialogFlow API Client
# for user/account logged in having used 'gcloud auth application-default login'

@pytest.fixture
def client():
    app = create_app()  
    return app.test_client()

# webhook end-to-end test
def test_webhook_with_case_data(client):
    request_data = {
        "sessionInfo": {
            "parameters": {
                "case_id": "123ABC"
            }
        },
        "fulfillmentInfo": {
            "tag": "Check Case Status"
        }
    }

    response = client.post("/webhook", json=request_data)

    assert response.status_code == 200
    assert "fulfillment_response" in response.get_json()