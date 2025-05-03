from flask import Blueprint, request, jsonify

sms_bp = Blueprint("sms_bp", __name__)

@sms_bp.route("/sms", methods=["POST"])
def sms_handler():
    from ..services.dialogflow_service import detect_intent_text

    session_id = request.form.get("From")
    user_message = request.form.get("Body")

    response = detect_intent_text(session_id=session_id, text=user_message)
    return jsonify({"fulfillment_text": response.response_messages[0].text.text[0]})

