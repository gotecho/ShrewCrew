from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.dialogflow_cx import detect_intent_text

main = Blueprint('main', __name__)

@main.route('/sms', methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body')
    sender_number = request.form.get('From')

    if not incoming_msg:
        return jsonify({"error": "No message received"}), 400

    # Send message to Dialogflow CX
    dialogflow_response = detect_intent_text(incoming_msg)

    # Prepare Twilio response
    twilio_response = MessagingResponse()
    twilio_response.message(dialogflow_response)

    return str(twilio_response)
