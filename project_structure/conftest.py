import pytest
from unittest.mock import patch, Mock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def patch_firestore_services():
    with patch("project_structure.config.get_credentials") as mock_creds, \
         patch("project_structure.config.get_firestore_client") as mock_client:

        mock_creds.return_value = Mock()
        mock_client.return_value = Mock()
        yield



