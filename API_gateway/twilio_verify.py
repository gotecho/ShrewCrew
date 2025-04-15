
from twilio.request_validator import RequestValidator
import os

def verify_twilio_request(request):
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    validator = RequestValidator(auth_token)

    url = request.url
    post_vars = request.form.to_dict()
    signature = request.headers.get('X-Twilio-Signature', '')

    return validator.validate(url, post_vars, signature)
