from flask import Blueprint, request, jsonify

webhook_bp = Blueprint("webhook_bp", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook_handler():
    from ..services.firestore_service import get_latest_request, save_request

    data = request.json
    case_id = data.get("case_id")
    issue = data.get("issue_description")

    if not get_latest_request(case_id):
        save_request(case_id, issue)

    return jsonify({"status": "received"}), 200
