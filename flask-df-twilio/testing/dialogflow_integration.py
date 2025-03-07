#Uses mock dialogflow API call to test if dialogflow responses are extracted correctly.
import pytest
from app.dialogflow_cx import detect_intent_text

@pytest.fixture
def mock_dialogflow_response(mocker):
    mock_response = mocker.Mock()
    mock_response.query_result.response_messages = [mocker.Mock()]
    mock_response.query_result.response_messages[0].text.text = ["Test Response"]
    
    mocker.patch("app.dialogflow_cx.client.detect_intent", return_value=mock_response)

def test_detect_intent_text(mock_dialogflow_response):
    response = detect_intent_text("Hello")
    assert response == "Test Response"

def test_detect_intent_empty_text(mock_dialogflow_response):
    """Tests how Dialogflow handles empty input."""
    response = detect_intent_text("")
    assert response == "No response from Dialogflow."

