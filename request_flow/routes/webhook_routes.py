from flask import Blueprint, request, jsonify
from request_flow.services.firestore_service import get_latest_request, save_request
from request_flow.services.salesforce_service import create_service_request, get_case_status

webhook_bp = Blueprint('webhook_bp', __name__)

# Fill in with API URL
SALESFORCE_URL = ""
# Fill in with our sf access token
ACCESS_TOKEN = ""

"""
Dialogflow CX webhook that checks Firestore and Salesforce 
to either look up a case status or start a new one
"""
@webhook_bp.route('/webhook/dialogflow', methods=['POST'])
def dialogflow_webhook():
    req = request.get_json()
    case_id = req["sessionInfo"]["parameters"].get("case_id")
    issue_description = req["sessionInfo"]["parameters"].get("issue_description", "No details provided")

    if not case_id:
        return jsonify({
            "fulfillmentResponse": {
                "messages": [{
                    "text": {"text": ["Missing Case ID."]}
                }]
            }
        })
    
    # Check for existing case ID in Firestore
    active_request = get_latest_request(case_id)

    if active_request:
        # Get status from SalesForce
        case_data = get_case_status(case_id)
        if "error" not in case_data:
            response_msg = f"Case {case_id} Status: {case_data['status']}\nDetails: {case_data['description']}"
        else:
            response_msg = "Case ID not found."
    else:
        # SalesForce creates new case ID
        sf_response = create_service_request(issue_description)
        if sf_response.get("case_id"):
            case_id = sf_response["case_id"]
            save_request(case_id, issue_description)
            response_msg = (
                f"Your service request has been created.\n"
                f"Case ID: {case_id}\n"
                f"Reply with 'CASE {case_id}' for updates."
            )
        else:
            response_msg = "Unable to submit request. Please try again."
    
    return jsonify({
        "fulfillmentResponse": {
            "messages": [{
                "text": {"text": [response_msg]}
            }]
        }
    })