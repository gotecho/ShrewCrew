import pytest
from unittest.mock import patch, MagicMock

# Start patches at import time so they're ready before any test loads the app
firestore_patch = patch("dialogflow_tools.playbook_tool_webhook.firestore.Client")
get_token_patch = patch("dialogflow_tools.playbook_tool_webhook.getToken", return_value="fake_token")
requests_post_patch = patch("dialogflow_tools.playbook_tool_webhook.requests.post")

# Activate mocks
mock_firestore = firestore_patch.start()
mock_get_token = get_token_patch.start()
mock_requests_post = requests_post_patch.start()

# Optional: Configure Firestore return mocks if needed
mock_firestore.return_value.collection.return_value.add.return_value = None

# Default mock Salesforce response
mock_requests_post.return_value.status_code = 200
mock_requests_post.return_value.json.return_value = {"success": True, "caseId": "mock123"}


@pytest.fixture
def client():
    from dialogflow_tools.playbook_tool_webhook import app
    app.testing = True
    return app.test_client()


def pytest_sessionfinish(session, exitstatus):
    # Clean up after the test run
    firestore_patch.stop()
    get_token_patch.stop()
    requests_post_patch.stop()

@pytest.fixture(autouse=True, scope="session")
def patch_firestore():
    with patch("dialogflow_tools.playbook_tool_webhook.firestore.Client") as mock_firestore:
        mock_instance = MagicMock()
        mock_firestore.return_value = mock_instance
        mock_instance.collection.return_value.add.return_value = None
        yield  # let the tests run