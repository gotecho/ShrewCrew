import pytest
from unittest.mock import patch, MagicMock
from request_flow.services.dialogflow_service import detect_intent_text


# Prevent actual API calls
@pytest.fixture
def mock_dialogflow():
    with patch("request_flow.services.dialogflow_service.client") as mock_client:
        yield mock_client


# test standard dialogflow response
def test_detect_intent_text(mock_dialogflow: MagicMock):
    mock_session_client = mock_dialogflow.session_path
    mock_detect_intent = mock_dialogflow.detect_intent

    # mock full Dialogflow response
    mock_response = MagicMock()
    mock_query_result = MagicMock()
    mock_query_result.response_messages = [MagicMock(text=MagicMock(text=["Hello!"]))]
    mock_query_result.intent = MagicMock(display_name="GreetingIntent")
    mock_query_result.language_code = "en"
    mock_response.query_result = mock_query_result

    mock_detect_intent.return_value = mock_response

    # simulate user query
    result = detect_intent_text("Hi")

    # check for expected response
    assert result == "Hello!"

    # ensure that the API call was made exactly once
    mock_session_client.assert_called_once()
    mock_detect_intent.assert_called_once()


# test if no response from Dialogflow
def test_detect_intent_text_no_response(mock_dialogflow: MagicMock):
    mock_detect_intent = mock_dialogflow.detect_intent

    # mock Dialogflow response with no response_messages
    mock_response = MagicMock()
    mock_query_result = MagicMock()
    mock_query_result.response_messages = []
    mock_response.query_result = mock_query_result

    mock_detect_intent.return_value = mock_response

    # simulate user query
    result = detect_intent_text("Hi")

    # check for fallback response
    assert result == "No response from Dialogflow."

    # ensure that the API call was made exactly once
    mock_detect_intent.assert_called_once()
    

# helper function for testing API failures
def assert_dialogflow_error_handling(mock_detect_intent, exception_message):
    # simulate API failure by raising an exception
    mock_detect_intent.side_effect = Exception(exception_message)

    # simulate user query
    result = detect_intent_text("Hi")

    # check for fallback error response
    assert result == "Error communicating with Dialogflow."

    # ensure that the API call was attempted
    mock_detect_intent.assert_called_once()
    

# test handling API failure -> network error
def test_detect_intent_text_api_failure(mock_dialogflow: MagicMock):
    assert_dialogflow_error_handling(mock_dialogflow.detect_intent, "Network error: Connection timed out")


# test handling API authentication failure
def test_detect_intent_text_auth_failure(mock_dialogflow: MagicMock):
    assert_dialogflow_error_handling(mock_dialogflow.detect_intent, "Unauthorized: Invalid credentials")


# test handling unexpected API exception
def test_detect_intent_text_unexpected_exception(mock_dialogflow: MagicMock):
    assert_dialogflow_error_handling(mock_dialogflow.detect_intent, "Unexpected error occurred")