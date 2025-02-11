import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from flask import Flask, request, Response  # type: ignore
from twilio.twiml.messaging_response import MessagingResponse
from msg_receive import fetch_sms


app = Flask(__name__)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# service_request_session = {}

# Initialize Firebase
credentials = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(credentials)
# Reference the Firestore database
database = firestore.client()

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

def verify_service_request(message):
    return message.startswith('Service Request:')
    # 'Service Request' can be changed to something else if need be

def save_service_request(phone_number, request_type, status="Pending"):
    """Save a new service request to Firestore"""
    doc_ref = db.collection("service_requests").document(phone_number)
    doc_ref.set({
        "phone_number": phone_number,
        "request_type": request_type,
        "status": status
    })

def update_request_status(phone_number, new_status):
    """Update the status of an existing request in Firestore"""
    doc_ref = db.collection("service_requests").document(phone_number)
    doc_ref.update({"status": new_status})

@app.route('/sms', methods=['POST'])
def request_response():
    received_sms = request.form.get('Body', '').strip().lower()
    # Option to get and retain user phone numbers for database purposes
    user_phone_number = request.form.get('From', '') 
    resp = MessagingResponse()

    # Check Firestore for an existing request
    doc_ref = db.collection("service_requests").document(user_phone_number)
    request_data = doc_ref.get()

    if request_data.exists:
        data = request_data.to_dict()
        curr_state = data.get("status")

        if curr_state == "active":
            resp.message("You currently have an active service request. What would you like to know?")
        elif curr_state == "awaiting_animal_info":
            resp.message("Thank you for providing additional details. Your request is being processed.")
            update_request_status(user_phone_number, "completed")
        elif curr_state == "completed":
            resp.message("Your service request is complete. Thank you for using Sacramento 311.")
        elif received_sms == "done":
            resp.message("Thank you for using Sacramento 311. Goodbye!")
            doc_ref.delete()
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
            request_entry = db.collection("service_requests").document(user_phone_number).get()
            if request_entry.exists:
                data = request_entry.to_dict()
                resp.message(f"Your request ({data['request_type']}) is currently: {data['status']}.")
            else:
                resp.message("No active service request found.")
        else:
            resp.message("Invalid request format. Please use: 'Service Request: [your request]'")

    return Response(str(resp), mimetype='text/xml')