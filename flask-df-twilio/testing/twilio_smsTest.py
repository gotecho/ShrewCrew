#Test to ensure send_sms() from twilio_sms.py correctly sends messages.
import pytest
from app.twilio_sms import send_sms

def test_send_sms(mocker):
    mock_twilio_client = mocker.patch("app.twilio_sms.Client")
    mock_message = mock_twilio_client.return_value.messages.create.return_value
    mock_message.sid = "mocked_sid"

    sid = send_sms("+1234567890", "Test message")

    assert sid == "mocked_sid"
    mock_twilio_client.return_value.messages.create.assert_called_once_with(
        body="Test message",
        from_="+1234567890",
        to="+1234567890"
    )

def test_send_sms_invalid_number(mocker):
    """Tests Twilio error handling when an invalid number is used."""
    mock_twilio_client = mocker.patch("app.twilio_sms.Client")
    mock_twilio_client.return_value.messages.create.side_effect = Exception("Invalid Number")

    with pytest.raises(Exception, match="Invalid Number"):
        send_sms("+000", "Test message")

