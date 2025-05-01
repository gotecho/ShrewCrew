import pytest
from app.dialogflow_cx import detect_intent_text, get_dialogflow_client


@pytest.fixture(autouse=True)
def mock_credentials(mocker):
    mocker.patch(
        "app.dialogflow_cx.service_account.Credentials.from_service_account_file"
    )


@pytest.fixture
def mock_dialogflow_response(mocker):
    mock_response = mocker.Mock()
    mock_response.query_result.response_messages = [mocker.Mock()]
    mock_response.query_result.response_messages[0].text.text = ["Test Response"]

    mock_client = mocker.Mock()
    mock_client.session_path.return_value = (
        "projects/fake/locations/fake/agents/fake/sessions/fake"
    )
    mock_client.detect_intent.return_value = mock_response
    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)


def test_detect_intent_text(mocker):
    """Covers the full successful path through detect_intent_text."""
    mock_response = mocker.Mock()
    message = mocker.Mock()
    message.text.text = ["Test Response"]
    mock_response.query_result.response_messages = [message]

    mock_client = mocker.Mock()
    mock_client.session_path.return_value = "projects/fake/locations/fake/agents/fake/sessions/fake"
    mock_client.detect_intent.return_value = mock_response

    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)

    response = detect_intent_text("Hello", session_id="test-session")
    assert response == "Test Response"



def test_detect_intent_empty_text(mocker):
    """Tests how Dialogflow handles empty input without hitting the API."""
    mock_client = mocker.Mock()
    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)
    response = detect_intent_text("", session_id="test-session")
    assert response == "No response from Dialogflow."


def test_detect_intent_text_empty_list(mocker):
    """Tests handling of an empty text list in response."""
    mock_response = mocker.Mock()
    mock_message = mocker.Mock()
    mock_message.text.text = []
    mock_response.query_result.response_messages = [mock_message]

    mock_client = mocker.Mock()
    mock_client.session_path.return_value = "fake/path"
    mock_client.detect_intent.return_value = mock_response

    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)

    response = detect_intent_text("empty", session_id="abc")
    assert "Dialogflow error" in response


def test_detect_intent_text_none_response_messages(mocker):
    """Tests handling when response_messages is None."""
    mock_response = mocker.Mock()
    mock_response.query_result.response_messages = None

    mock_client = mocker.Mock()
    mock_client.session_path.return_value = "fake/path"
    mock_client.detect_intent.return_value = mock_response

    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)

    response = detect_intent_text("none", session_id="abc")
    assert "Dialogflow error" in response


def test_detect_intent_exception(mocker):
    """Tests that errors in detect_intent_text are caught and return a fallback message."""
    mock_client = mocker.Mock()
    mock_client.session_path.side_effect = Exception("session fail")
    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)

    response = detect_intent_text("Hello", session_id="test-session")
    assert "Dialogflow error: session fail" in response

def test_detect_intent_text_no_text_field(mocker):
    """Tests fallback when response message has no .text field."""
    mock_message = mocker.Mock()
    mock_message.text = None  # simulate message without .text

    mock_response = mocker.Mock()
    mock_response.query_result.response_messages = [mock_message]

    mock_client = mocker.Mock()
    mock_client.session_path.return_value = "fake/path"
    mock_client.detect_intent.return_value = mock_response

    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)

    response = detect_intent_text("no text field", session_id="abc")
    assert response == "No response from Dialogflow."

def test_get_dialogflow_client(mocker):
    """Tests that get_dialogflow_client returns an instance of SessionsClient (mocked)."""
    class MockSessionsClient:
        def __init__(self, credentials=None, client_options=None):
            self.name = "MockSessionClient"

    mocker.patch(
        "google.cloud.dialogflowcx_v3.SessionsClient",
        return_value=MockSessionsClient()
    )

    client = get_dialogflow_client()

    assert isinstance(client, MockSessionsClient)
    assert client.name == "MockSessionClient"



