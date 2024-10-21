from twilio.rest import Client
from flask import Flask, request, redirect # type: ignore
from twilio.twiml.messaging_response import MessagingResponse
import twilio_acct_info

app = Flask(__name__)

'''
The following function will take an SMS message sent from the client
to our Twilio phone number and verify whether or not it's an acceptable 
service request for our 311 text channel to handle.
'''
def verify_service_request(message):
    return message.startswith('Service Request:')
    # 'Service Request' can be changed to something else if need be

client = Client(twilio_acct_info.acct_sid, twilio_acct_info.acct_auth_tok)

def sms_reply():
    # Get the message from the client
    received_sms =  request.values.get('Body', '')
    # Get the client's phone number from message
    client_number = request.values.get('From', '')

    resp = MessagingResponse()

    if verify_service_request(received_sms):
       resp.message('Your service request has been received. '
                    + 'The following details are required: ....')
                    # We can fine tune this as the project progresses
    else:
        resp.message('Please use the correct format. '
                     + 'Example - Service Request: Dead animal found '
                     + 'at 123 XYZ Street.')

    return str(resp)