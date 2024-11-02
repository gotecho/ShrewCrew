#python 3.6+ required
#ENSURE YOU HAVE TWILIO INSTALLED IN YOUR MACHINE! THIS PROGRAM WON'T WORK OTHERWISE!
#Not sure how to get around this.
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessageResponse
from Testing_Files import gemini_testing
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
# Ava: I want to add a sms function to use FLASK. Need to consult team. 
app = Flask(__name__)


value_of_sid='sacCitySID' #Use SID of Sacramento City account provided in email
value_of_auth='sacCityAuthToken' #Auth Token of Sacramento City Account

account_sid = os.environ["TWILIO_ACCOUNT_SID"]=value_of_sid
auth_token = os.environ["TWILIO_AUTH_TOKEN"]=value_of_auth
client = Client(account_sid, auth_token)
@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_message = request.form['Body']
    gemini_response = gemini_testing.generate_gemini_response(incoming_message) # Trying to send twilio message to gemini
    resp = MessageResponse()
    resp.message(gemini_response.text)
    print(resp)
    return str(resp)


message = client.messages.create(
    body="Join Earth's mightiest heroes. Like Kevin Bacon.", #Example Message, change to whatever you want to send
    from_="+1 916 914 8824", #Number provided by Sacramento City
    to="+1 916 693 0232", #my own number, can change to your number if you need to for testing
)

