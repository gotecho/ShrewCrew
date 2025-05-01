# testing/test_twilio_smsTest.py

import os
import pytest
from flask import Flask
from app.twilio_sms import send_sms, verify_twilio_request


def test_send_sms(mocker):
    mocker.patch.dict(os.environ, {
        "TWILIO_PHONE_NUMBER": "+1234567890",
        "TWILIO_ACCOUNT_SID": "dummy_sid",
        "TWILIO_AUTH_TOKEN": "dummy_token"
    })

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


def test_verify_twilio_request_valid(mocker):
    app = Flask(__name__)
    mocker.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "test_token"})

    mock_validator = mocker.patch("app.twilio_sms.TwilioRequestValidator")
    mock_validator.return_value.validate.return_value = True

    with app.test_request_context(headers={"X-Twilio-Signature": "fake"}):
        # Should not raise error if valid
        verify_twilio_request()


def test_verify_twilio_request_invalid_signature(mocker):
    app = Flask(__name__)
    mocker.patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "test_token"})

    mock_validator = mocker.patch("app.twilio_sms.TwilioRequestValidator")
    mock_validator.return_value.validate.return_value = False

    with app.test_request_context(headers={"X-Twilio-Signature": "fake"}):
        with pytest.raises(Exception) as exc_info:
            verify_twilio_request()
        assert "Request not from Twilio." in str(exc_info.value)


def test_send_sms_fails_without_number(mocker):
    # Clear all environment variables for this test
    mocker.patch.dict(os.environ, {}, clear=True)

    # Patch Client to prevent any real initialization
    mocker.patch("app.twilio_sms.Client")

    with pytest.raises(ValueError, match="TWILIO_PHONE_NUMBER is not set in environment variables."):
        send_sms("+1234567890", "Hello")

def test_verify_twilio_request_missing_token(monkeypatch):
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    with pytest.raises(Exception, match="TWILIO_AUTH_TOKEN is not set in environment variables"):
        verify_twilio_request()


