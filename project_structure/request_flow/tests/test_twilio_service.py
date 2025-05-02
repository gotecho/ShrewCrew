import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import pytest
import os
import re
from unittest.mock import MagicMock, patch
from request_flow.services.twilio_service import send_sms

# prevent actual API calls
@pytest.fixture
def mock_twilio():
    with patch("request_flow.services.twilio_service.client") as mock_client:
        yield mock_client


# test to validate phone number is in E.164 format
def is_valid_phone_number(phone_number):
    e164_regex = re.compile(r"^\+\d{10,15}$")  
    return bool(e164_regex.match(phone_number))
    

# test for the above phone number format validation
def test_phone_number_format():
    valid_numbers = ["+1234567890", "+15551234567", "+447911123456"]
    invalid_numbers = ["1234567890", "555-1234", "+1(555)123-4567", "abcd1234"]

    for number in valid_numbers:
        assert is_valid_phone_number(number) is True, f"Expected {number} to be valid"

    for number in invalid_numbers:
        assert is_valid_phone_number(number) is False, f"Expected {number} to be invalid"


def test_send_sms(mock_twilio: MagicMock):
    # reset mock before execution
    mock_twilio.reset_mock()

    # mock client.messages.create
    mock_messages = mock_twilio.messages.create
    # fake message ID
    mock_messages.return_value.sid = "SM123456789"

    test_number = "+1234567890"
    test_message = "Test message"
    fake_twilio_number = "+1987654321"

    # mock environment variable
    with patch.dict(os.environ, {"TWILIO_PHONE_NUMBER": fake_twilio_number}):
        result = send_sms(test_number, test_message)

    # Ensure expected output
    assert result == "SM123456789"

    # Ensure correct arguments are called
    mock_messages.assert_called_once_with(
        body=test_message,
        from_=fake_twilio_number,
        to=test_number
    )


# function to simulate errors
def test_send_sms_error(mock_twilio: MagicMock):
    # reset mock before execution
    mock_twilio.reset_mock()

    mock_messages = mock_twilio.messages.create

    # raise exception for client.messages.create -> failure
    mock_messages.side_effect = Exception("Twilio API error")

    test_number = "+1234567890"
    test_message = "Test message"
    fake_twilio_number = "+1987654321"

    # mock environment variable
    with patch.dict(os.environ, {"TWILIO_PHONE_NUMBER": fake_twilio_number}):
        # expect and handle error
        result = send_sms(test_number, test_message)

    # if error occurs, None is returned
    assert result is None

    # ensure that client.messages.create was attempted
    mock_messages.assert_called_once_with(
        body=test_message,
        from_=fake_twilio_number,
        to=test_number
    )