import pytest
from app.dialogflow_cx import detect_intent_text

@pytest.fixture(autouse=True)
def mock_credentials(mocker):
    mocker.patch(
        "app.dialogflow_cx.service_account.Credentials.from_service_account_file"
    )

@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock()
    client.session_path.return_value = "projects/fake/locations/fake/agents/fake/sessions/fake"
    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=client)
    return client

def test_detect_intent_text_normal(mock_client):
    mock_response = mock_client.detect_intent.return_value
    mock_response.query_result.response_messages = [m := mock_client.Mock()]
    m.text.text = ["Hello from DF"]
    
    response = detect_intent_text("Hi", session_id="abc")
    assert response == "Hello from DF"

def test_detect_intent_text_empty_list(mock_client):
    mock_response = mock_client.detect_intent.return_value
    mock_response.query_result.response_messages = [m := mock_client.Mock()]
    m.text.text = []
    
    response = detect_intent_text("empty", session_id="abc")
    assert response == "No response from Dialogflow."

def test_detect_intent_text_none_response_messages(mock_client):
    mock_response = mock_client.detect_intent.return_value
    mock_response.query_result.response_messages = None
    
    response = detect_intent_text("none", session_id="abc")
    assert response == "No response from Dialogflow."

def test_detect_intent_text_exception(mocker):
    mock_client = mocker.Mock()
    mock_client.session_path.side_effect = Exception("session fail")
    mocker.patch("app.dialogflow_cx.get_dialogflow_client", return_value=mock_client)

    with pytest.raises(Exception, match="session fail"):
        detect_intent_text("fail", session_id="abc")


