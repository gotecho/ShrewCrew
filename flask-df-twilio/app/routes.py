from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.dialogflow_cx import detect_intent_text
from app.twilio_sms import verify_twilio_request
import logging

main = Blueprint('main', __name__)

@main.route('/sms', methods=['POST'])
def sms_reply():
    verify_twilio_request()

    try:
        logging.info('Incoming request to sms_reply')

        incoming_msg = request.form.get('Body')
        sender_number = request.form.get('From')

        if not incoming_msg:
            return jsonify({"error": "No message received"}), 400

        session_id = sender_number
        dialogflow_response = detect_intent_text(incoming_msg, session_id)

        twilio_response = MessagingResponse()
        twilio_response.message(dialogflow_response)

        logging.info('Successfully processed sms_reply')
        return str(twilio_response)

    except Exception as e:
        logging.exception('Error in sms_reply')
        twilio_response = MessagingResponse()
        twilio_response.message("No response from Dialogflow.")
        return str(twilio_response), 200
