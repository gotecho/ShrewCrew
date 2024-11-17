import os
from flask import Flask, request, jsonify, render_template, abort, Response
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import SyncGrant
load_dotenv()

app = Flask(__name__)
twilio_client = Client()


@app.route('/dashboard', methods=['GET'])
def view_dashboard():
    return render_template('index.html')


@app.route('/inbound/sms', methods=['POST'])
def inbound_sms():
    data = {
        'MessageSid': request.form['MessageSid'],
        'From': request.form['From'],
        'To': request.form['To'],
        'Message': request.form['Body']
    }
    twilio_sync_service = twilio_client.sync.services(os.environ['TWILIO_SERVICE_SID'])
    sync_list_item = twilio_sync_service.sync_lists('twilio_incoming_sms').sync_list_items.create(data=data)
    return Response()


@app.route('/token', methods=['GET'])
def generate_token():
    username = request.args.get('username')
    if not username:
        abort(401)
    # Create a grant identifying the Sync instance for this app
    sync_grant = SyncGrant(os.environ['TWILIO_SERVICE_SID'])
    # Create an access token which we will sign and return to the client, containing the grant we just created and specifying the identity
    token = AccessToken(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_API_KEY'], os.environ['TWILIO_API_SECRET'])
    token.add_grant(sync_grant)
    token.identity = username

    return jsonify(identity=username, token=token.to_jwt().decode())


if __name__ == '__main__':
    app.run()