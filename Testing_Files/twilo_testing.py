#python 3.6+ required
#ENSURE YOU HAVE TWILIO INSTALLED IN YOUR MACHINE! THIS PROGRAM WON'T WORK OTHERWISE!
#Not sure how to get around this.
import os
from dotenv import load_dotenv
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import gemini_testing
load_dotenv()
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
app = Flask(__name__)


value_of_sid= os.getenv("TWILIO_SID") #Use SID of Sacramento City account provided in email
value_of_auth=os.getenv("TWILIO_AUTH") #Auth Token of Sacramento City Account

account_sid = os.environ["TWILIO_ACCOUNT_SID"]=value_of_sid
auth_token = os.environ["TWILIO_AUTH_TOKEN"]=value_of_auth
client = Client(account_sid, auth_token)
@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_message = request.form['Body']
    print(f"Incoming message: {incoming_message}")
    gemini_response = gemini_testing.generate_gemini_response(incoming_message) # Trying to send twilio message to gemini
    resp = MessagingResponse()
    resp.message(gemini_response)
    print(f"twilio response: {str(resp)}")
    return str(resp)

twilio_phone_number = "+1 916 914 8824"

webhook_url = 'https://556a-98-41-39-122.ngrok-free.app/sms' # My ngrok local url with flask's /sms
client = Client(account_sid, auth_token)

phone_number = client.incoming_phone_numbers.list(phone_number=twilio_phone_number)[0]
phone_number.update(sms_url=webhook_url) # lists phone numbers associated with twilio account. 
# Updates webhook URL that wilio will use when a message is received at provided phone number.

print(f"Webhook URL for {twilio_phone_number} updated to {webhook_url}")

if __name__ == "__main__":
    app.run(debug=True)
