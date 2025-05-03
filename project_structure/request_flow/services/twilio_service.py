from project_structure.config import get_twilio_config
twilio_config = get_twilio_config()

from twilio.rest import Client

client = Client(twilio_config['sid'], twilio_config['auth_token'])

def send_sms(to, message):
    try:
        sms = client.messages.create(
            body=message,
            to=to,
            from_=twilio_config['phone']
        )
        return sms.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
