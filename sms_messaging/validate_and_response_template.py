import os
import firebase_admin
import datetime
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# validate
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("Twilio account credentials missing.")

app = Flask(__name__)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize Firebase
creds = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(creds)

# Firestore database
database = firestore.client()

# Dictionary of responses (this is just for example so this part can be altered or deleted)
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
    return 'service request:' in message.lower()
    # Check if message is actually a service request
    # This is technically arbritary in checking for requests, so this is essentially
    # a base case setup function
    # 'Service Request' can be changed to something else if need be


def save_service_request(phone_number, request_type, status="Pending"):
    """Save a new service request to Firestore"""
    try:
        doc_ref = database.collection("service_requests").document()
        # allow Firestore to auto-generate user IDs
        doc_id = doc_ref.id
        doc_ref.set({
            "request_id": doc_id,
            "phone_number": phone_number,
            "request_type": request_type,
            "status": status,
            "timestamp": datetime.datetime.now()
        })
    except Exception as e:
        print(f"Unable to save service request: {e}")


def update_request_status(request_id, new_status):
    """Update the status of an existing request in Firestore"""
    try:
        doc_ref = database.collection("service_requests").document(request_id)
        doc_ref.update({"status": new_status})
    except Exception as e:
        print(f"Unable to update service request status: {e}")


@app.route('/sms', methods=['POST'])
def request_response():
    # handle messages from Twilio
    received_sms = request.form.get('Body', '').strip().lower()
    # get and retain user phone numbers for database purposes
    user_phone_number = request.form.get('From', '') 
    resp = MessagingResponse()

    # check for other possible service requests tied to user's phone number
    requests_query = database.collection("service_requests") \
        .where("phone_number", "==", user_phone_number).get() \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .limit(1).get()

    active_request = None
    if len(requests_query) > 0:
        data = requests_query[0].to_dict()
        if data.get("status") in ["active", "awaiting_animal_info"]:
            active_request = data

    if active_request:
        request_id = active_request["request_id"]
        curr_state = active_request["status"]

        if curr_state == "active":
            resp.message("You currently have an active service request. What would you like to know?")
        elif curr_state == "awaiting_animal_info":
            resp.message("Thank you for providing additional details. Your request is being processed.")
            update_request_status(request_id, "completed")
        elif curr_state == "completed":
            resp.message("Your service request is complete. Thank you for using Sacramento 311.")
        elif received_sms == "done":
            resp.message("Thank you for using Sacramento 311. Goodbye!")
            database.collection("service_requests").document(request_id).delete()
    else:
        if verify_service_request(received_sms):
            matched = False
            for keyphrase, response_msg in animal_care_request_options.items():
                if keyphrase in received_sms:
                    resp.message(response_msg)
                    save_service_request(user_phone_number, keyphrase, "awaiting_animal_info")
                    matched = True
                    break
            if not matched:
                resp.message("Invalid request. Please type 'menu' for options.")
        elif received_sms == "status":
            if len(requests_query) > 0:
                latest_request = requests_query[0].to_dict()
                resp.message(f"Your request ({latest_request['request_type']}) is currently: {latest_request['status']}.")
            else:
                resp.message("No active service request found.")
        else:
            resp.message("Invalid request format. Please use: 'Service Request: [your request]'")

    return Response(str(resp), mimetype='text/xml')