import os
import requests
import logging
from project_structure.config import get_salesforce_credentials

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def authenticate_salesforce():
    sf_creds = get_salesforce_credentials()

    url = f"{sf_creds['instance_url']}/services/oauth2/token"
    payload = {
        "grant_type": "password",
        "client_id": sf_creds["client_id"],
        "client_secret": sf_creds["client_secret"],
        "username": sf_creds["username"],
        "password": sf_creds["password"] + sf_creds["security_token"]
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        logging.error(f"Salesforce OAuth failed: {response.status_code} - {response.text}")
        raise Exception("Salesforce authentication failed.")

    token_data = response.json()
    logging.info("Salesforce OAuth authentication successful.")
    return {
        "access_token": token_data["access_token"],
        "instance_url": token_data["instance_url"]
    }

def create_service_request(issue_description):
    try:
        auth = authenticate_salesforce()
        headers = {
            "Authorization": f"Bearer {auth['access_token']}",
            "Content-Type": "application/json"
        }

        case_data = {
            "Subject": "New 311 Service Request",
            "Description": issue_description,
            "Status": "New"
        }

        response = requests.post(
            f"{auth['instance_url']}/services/data/v58.0/sobjects/Case",
            json=case_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            case_id = response.json().get("id")
            logging.info(f"Salesforce case created: {case_id}")
            return {"case_id": case_id, "message": "Case created successfully."}
        else:
            logging.error(f"Salesforce case creation failed: {response.text}")
            return {"error": f"Failed to create case: {response.text}"}
    except Exception as e:
        logging.error(f"Exception during Salesforce case creation: {e}")
        return {"error": str(e)}

def get_case_status(case_id):
    try:
        auth = authenticate_salesforce()
        headers = {
            "Authorization": f"Bearer {auth['access_token']}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{auth['instance_url']}/services/data/v58.0/sobjects/Case/{case_id}",
            headers=headers
        )

        if response.status_code == 200:
            case_data = response.json()
            return {
                "status": case_data.get("Status", "Unknown"),
                "description": case_data.get("Description", "No details available.")
            }
        elif response.status_code == 404:
            return {"error": "Case not found."}
        else:
            return {"error": f"Error retrieving case: {response.text}"}
    except Exception as e:
        logging.error(f"Exception during case retrieval: {e}")
        return {"error": str(e)}