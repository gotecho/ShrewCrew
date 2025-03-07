#Simulates an end to end message cycle to ensure Twilio and Dialogflow work together.
def test_sms_reply_integration(mocker, client):
    
    mocker.patch("app.dialogflow_cx.detect_intent_text", return_value="Test Response")

    response = client.post("/sms", data={"Body": "Hello", "From": "+1234567890"})

    assert response.status_code == 200
    assert "<Response><Message>Test Response</Message></Response>" in response.get_data(as_text=True)
