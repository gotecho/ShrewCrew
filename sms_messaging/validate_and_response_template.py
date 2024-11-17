from dotenv import load_dotenv
from flask import Flask, request, Response  # type: ignore
from twilio.twiml.messaging_response import MessagingResponse
from msg_receive import fetch_sms

app = Flask(__name__)

client = Client(twilio_acct_info.acct_sid, twilio_acct_info.acct_auth_tok)

# Dictionary of responses
animal_care_request_options = {
    'dead animal': 'Thank you for reporting the sighting of a dead animal on '
    + 'a public right-of-way. We\'ll get an Animal Control Officer to respond '
    + 'to your service request as soon as possible.',
    'pet complaint or concern': 'Thank you for reporting your complaint '
    + 'or concern for an owned animal. Please provide the following information: ',
    'stray or loose animal' : 'Thank you for reporting a stray or loose animal. '
    + 'We\'ll get an Animal Control Officer to respond as soon as possible.',
    'animal shelter' : 'Questions about adoptions, spay/neuter resources, '
    + 'found animals, licensing and barking are directed to the Front Street '
    + 'Shelter. Please provide the following information: ',
    'animal control' : 'Thank you for reporting your animal control '
    + 'request. Please provide the following information: '
}

def verify_service_request(message):
    return message.startswith('Service Request:')
    # 'Service Request' can be changed to something else if need be

@app.route('/sms', methods=['POST'])
def request_response():
    received_sms = request.form.get('Body', '').strip().lower()
    # Option to get and retain user phone numbers for database purposes
    # user_phone_number = request.form.get('From', '') 
    resp = MessagingResponse()

    if verify_service_request(received_sms):
        for keyphrase, response_msg in animal_care_request_options.items():
            if keyphrase in received_sms:
                resp.message(response_msg)
                break
            else:
                resp.message('Thank you for using Sacramento\'s 311 text '
                         + 'channel. For a list of Animal Care Request '
                         + 'options, please type "menu".')
    else:
        resp.message('Your message is not a valid service request. Please '
                     + 'use the following format: "Service Request: '
                      + '[your service request]"')
    
    return Response(str(resp), mimetype = 'text/xml')