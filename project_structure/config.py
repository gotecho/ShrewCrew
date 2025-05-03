from google.oauth2 import service_account
from google.cloud import firestore
import os

def get_credentials():
    print("Loading credentials...")
    return service_account.Credentials.from_service_account_file("fake-credentials.json")

def get_firestore_client():
    print("Getting Firestore client...")
    return firestore.Client(credentials=get_credentials())

def get_application_credentials():
    return os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "fake-credentials.json")

def get_project_id():
    return os.getenv("GCP_PROJECT_ID", "test-project")

def get_region():
    return os.getenv("DIALOGFLOW_REGION", "us-central1")

def get_agent_id():
    return os.getenv("DIALOGFLOW_AGENT_ID", "test-agent-id")

def get_salesforce_credentials():
    return {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "username": "your_username",
        "password": "your_password",
        "security_token": "your_token"
    }



