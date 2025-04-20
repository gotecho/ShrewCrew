from config import database
import datetime
import logging
import uuid
import hashlib

# Configure logging
logging.basicConfig(
    filename="logs/firestore.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Fetch the latest service request using case_id instead of a phone_number.
def get_latest_request(case_id):
    try:
        logging.info(f"Fetching latest request for case_id: {case_id}")
        requests_query = database.collection("service_requests") \
            .where("case_id", "==", case_id) \
            .order_by("timestamp", direction="DESCENDING") \
            .limit(1).get()
        
        if requests_query:
            request_data = requests_query[0].to_dict()
            logging.info(f"Request found: {request_data}")
            return request_data
        else:
            logging.info(f"No data found for case_id: {case_id}")
            return None
    except Exception as e:
        logging.error(f"Error fetching request for case_id {case_id}: {e}")
        return None


# Stores a new request in Firestore using case_id instead of a phone number.
def save_request(case_id, issue_description):
    try:
        doc_ref = database.collection("service_requests").document(case_id)
        request_data = {
            "case_id": case_id,
            "issue_description": issue_description,
            "timestamp": datetime.datetime.utcnow()
        }
        doc_ref.set(request_data)
        logging.info(f"New request saved: {request_data}")
    except Exception as e:
        logging.error(f"Error saving request for case_id {case_id}: {e}")
        

def get_all_cases():
    cases_ref = database.collection("service_requests")
    docs = cases_ref.stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]


# Updates the status of an existing request in Firestore.
def update_request_status(case_id, new_status):
    try:
        doc_ref = database.collection("service_requests").document(case_id)
        doc_ref.update({"status": new_status})
        logging.info(f"Updated status for case_id {case_id} to {new_status}")
    except Exception as e:
        logging.error(f"Error updating status for case_id {case_id}: {e}")


# Deletes a request from Firestore.
def delete_request(case_id):
    try:
        database.collection("service_requests").document(case_id).delete()
        logging.info(f"Deleted request for case_id {case_id}")
    except Exception as e:
        logging.error(f"Error deleting request for case_id {case_id}: {e}")


# Implement Firestore conversation logs
def log_message(user, message, direction="inbound"):
    try:
        doc_ref = database.collection("conversations").document(user)
        doc_ref.collection("messages").add({
            "message": message,
            "direction": direction,
            "timestamp": datetime.datetime.utcnow()
        })
    except Exception as e:
        logging.error(f"Error logging message for user {user}: {e}")

def generate_session_id():
    raw_uuid = str(uuid.uuid4())
    return hashlib.md5(raw_uuid.encode()).hexdigest()


def set_user_session(phone_number, session_id):
    try:
        database.collection("sessions").document(phone_number).set({
            "session_id": session_id,
            "timestamp": datetime.datetime.utcnow()
        })
        logging.info(f"Session ID set for {phone_number}: {session_id}")
    except Exception as e:
        logging.error(f"Error setting session for {phone_number}: {e}")


def get_user_session(phone_number):
    try:
        doc = database.collection("sessions").document(phone_number).get()
        if doc.exists:
            data = doc.to_dict()
            session_id = data.get("session_id")
            timestamp = data.get("timestamp")

            if timestamp:
                time_diff = datetime.datetime.utcnow() - timestamp
                if time_diff.total_seconds() > 1800:  # 30 minutes
                    logging.info(f"Session expired for {phone_number}")
                    return None

            return session_id
        return None
    except Exception as e:
        logging.error(f"Error retrieving session for {phone_number}: {e}")
        return None