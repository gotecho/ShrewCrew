import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True, scope="session")
def patch_firestore():
    with patch("dialogflow_tools.playbook_tool_webhook.firestore.Client") as mock_firestore:
        mock_instance = MagicMock()
        mock_firestore.return_value = mock_instance
        mock_instance.collection.return_value.add.return_value = None
        yield  # let the tests run