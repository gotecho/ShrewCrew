from config import database
import datetime
import logging

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