from flask import Flask, request, Response # type: ignore
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

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

@app.route('/sms', methods=['POST'])
def request_response():
    incoming_msg = request.form.get('Body', '').strip().lower()
    resp = MessagingResponse()

    for keyphrase, response_msg in animal_care_request_options.items():
        if keyphrase in incoming_msg:
            resp.message(response_msg)
            break
    else:
        resp.message('Thank you for using Sacramento\'s 311 text '
                         + 'channel. For a list of Animal Care Request '
                         + 'options, please type \"menu\".')

    return Response(str(resp), mimetype='text/xml')
