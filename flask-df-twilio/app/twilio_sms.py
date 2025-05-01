import os
from twilio.rest import Client
from twilio.request_validator import RequestValidator as TwilioRequestValidator
from flask import request, abort
import logging

def verify_twilio_request():
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not auth_token:
        raise Exception("TWILIO_AUTH_TOKEN is not set in environment variables")

    validator = TwilioRequestValidator(auth_token)
    request_url = request.url
    request_params = request.form.to_dict()
    twilio_signature = request.headers.get("X-Twilio-Signature", "")

    if not validator.validate(request_url, request_params, twilio_signature):
        abort(403, description="Request not from Twilio.")

def send_sms(to_number, message):
    try:
        twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        if not twilio_phone_number:
            raise ValueError("TWILIO_PHONE_NUMBER is not set in environment variables.")

        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        message = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to_number
        )
        return message.sid

    except Exception as e:
        logging.exception("Error in twilio_sms function")
        raise
