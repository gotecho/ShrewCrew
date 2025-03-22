from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from request_flow.services.dialogflow_service import detect_intent_text
from request_flow.services.firestore_service import log_message

sms_bp = Blueprint('sms_bp', __name__)

"""
Incoming SMS messages from Twilio are handled and routed to/through
DialogFlow CX, SalesForce, and/or Firestore
"""
@sms_bp.route('/sms', methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body', '').strip().lower()
    sender_number = request.form.get('From', '')

    # base case
    if not incoming_msg:
        return jsonify({"error": "NO SMS RECEIVED"}), 400
    
    # log inbound SMS
    log_message(sender_number, incoming_msg, direction="inbound")
    
    response_msg = process_request(sender_number, incoming_msg)

    # log AI response
    log_message(sender_number, response_msg, direction="outbound")

    # set up Twilio
    twilio_resp = MessagingResponse()
    twilio_resp.message(response_msg)

    return str(twilio_resp)

# Handles incoming SMS and forwards info to DFCX for response
def process_request(sender_number, incoming_msg):
    return detect_intent_text(incoming_msg, sender_number)