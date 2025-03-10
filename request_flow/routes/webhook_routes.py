import requests
from flask import Blueprint, request, jsonify
from request_flow.services.firestore_service import get_latest_request, save_request

webhook_bp = Blueprint('webhook_bp', __name__)

# Fill in with API URL
SALESFORCE_URL = ""
# Fill in with our sf access token
ACCESS_TOKEN = ""

"""
Check Firestore if request/conversation is new or existing
"""
@webhook_bp.route('/webhook/dialogflow', methods=['POST'])
def dialogflow_webhook():
    req = request.get_json()
    case_id = req["sessionInfo"]["parameters"].get("case_id")
    issue_description = req["sessionInfo"]["parameters"].get("issue_description", "No details provided")

    if not case_id:
        return jsonify({"fulfillmentResonse": {"messages": [{"text": {"text": ["Missing Case ID."]}}]}})
    
    # Check for existing case ID
    active_request = get_latest_request(case_id)

    if active_request:
        response_msg = get_case_status(case_id)
    else:
        # Call to SalesForce which creates a new case ID
        case_id = create_new_case(issue_description)
        if case_id:
            # Store SF's newly generated case ID in Firestore 
            save_request(case_id, issue_description)
            response_msg = f"""Your service request has been created.\n 
                           Case ID: {case_id}\nReply with 'CASE {case_id}' 
                           for updates."""
        else:
            response_msg = "There was an issue submitting your request. Please try again."
    
    return jsonify({"fulfillmentResponse": {"messages": [{"text": {"text": [response_msg]}}]}})


# Search sf for the status of an existing case ID
def get_case_status(case_id):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

    response = requests.get(f"{SALESFORCE_URL}/{case_id}", headers=headers)

    if response.status_code == 200:
        case_data = response.json()
        status = case_data.get("Status", "Unknown")
        details = case_data.get("Description", "No details available.")
        return f"Case {case_id} Status: {status}\nDetails: {details}"
    return "Invalid Case ID or case not found."


# Use sf to create a new case and get the case ID
def create_new_case(description):
    new_case = {
        "Subject": "New 311 Request",
        "Description": description,
        "Status": "New",
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    # POST request to sf
    response = requests.post(SALESFORCE_URL, json=new_case, headers=headers)

    if response.status_code != 201:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    elif response.status_code == 201:
        # returns the case ID
        return response.json().get("id")