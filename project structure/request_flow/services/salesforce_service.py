from simple_salesforce import Salesforce, SalesforceAuthenticationFailed, SalesforceExpiredSession
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Authenticate creds and connect to sf
def authenticate_salesforce():
    try:
        sf = Salesforce(
            username=os.getenv("SALESFORCE_USERNAME"),
            password=os.getenv("SALESFORCE_PASSWORD"),
            #security_token=os.getenv("SALESFORCE_SECURITY_TOKEN")
            #security_token=os.getenv("SALESFORCE_SECRET_KEY")
            security_token=os.getenv("SALESFORCE_AUTH_URL")
        )
        logging.info("SalesForce authentication successful.")
        return sf
    except SalesforceAuthenticationFailed as e:
        logging.error(f"SalesForce authentication failed: {e}")
        return None
    
sf = authenticate_salesforce()


# Function to handle expired session. Refreshes token and retries authentication.
def retry_auth_and_request(func, *args):
    global sf
    try:
        return func(*args)
    except SalesforceExpiredSession:
        logging.warning("Salesforce session expired. Re-authenticating...")
        sf = authenticate_salesforce()
        if sf:
            return func(*args)
        else:
            return {"error": "Salesforce re-authentication failed."}
        

# Creates a new service request in Salesforce and returns the case ID.
def create_service_request(issue_description):
    try:
        case_data = {
            "Subject": "New 311 Service Request",
            "Description": issue_description,
            "Status": "New"
        }
        response = sf.Case.create(case_data)
        logging.info(f"Successfully created Salesforce case: {response['id']}")
        return {"case_id": response["id"], "message": "Case created successfully."}
    except SalesforceExpiredSession:
        return retry_auth_and_request(create_service_request, issue_description)
    except Exception as e:
        print(f"Error creating Salesforce case: {e}")
        return {"error": str(e)}
    

# Fetches the status of an existing Salesforce case using the case ID.
def get_case_status(case_id):
    try:
        case_record = sf.Case.get(case_id)
        logging.info(f"Retrieved case {case_id} status: {case_record.get('Status', 'Unknown')}")
        return {
            "status": case_record.get("Status", "Unknown"),
            "description": case_record.get("Description", "No details available.")
        }
    except SalesforceExpiredSession:
        return retry_auth_and_request(get_case_status, case_id)
    except Exception as e:
        logging.error(f"Error retrieving case status for {case_id}: {e}")
        return {"error": str(e)}