import os
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from flask import request, abort
import logging

def verify_twilio_request():
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not auth_token:
        raise Exception("TWILIO_AUTH_TOKEN is not set in environment variables")

    validator = RequestValidator(auth_token)
    request_url = request.url
    request_params = request.form.to_dict()
    twilio_signature = request.headers.get("X-Twilio-Signature", "")

    if not validator.validate(request_url, request_params, twilio_signature):
        abort(403, description="Request not from Twilio.")

def send_sms(to, message):
    try:
        logging.info('Entering twilio_sms function')

        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

        message = client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to
        )

        return message.sid

    except Exception as e:
        logging.exception('Error in twilio_sms function')
        raise