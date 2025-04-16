import os
from twilio.rest import Client

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Sends an SMS via Twilio.
def send_sms(to, message):
    try:
        sms = client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to
        )
        return sms.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None