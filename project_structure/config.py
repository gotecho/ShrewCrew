import os
from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv
#from pathlib import Path

load_dotenv()

# Firestore Database Setup
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GOOGLE_PROJECT_ID or not GOOGLE_APPLICATION_CREDENTIALS:
    raise ValueError("Required .env values not set")

# Resolve key path relative to config.py
CREDENTIALS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../sms_messaging", GOOGLE_APPLICATION_CREDENTIALS)
)
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)

database = firestore.Client(
    project=GOOGLE_PROJECT_ID,
    credentials=credentials,
    database="shrewcrew-database"
)

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    #GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")
    GOOGLE_LOCATION = os.getenv("REGION")

class SalesforceConfig:
    USERNAME = os.getenv("SALESFORCE_USERNAME")
    PASSWORD = os.getenv("SALESFORCE_PASSWORD")
    SECURITY_TOKEN = os.getenv("SALESFORCE_SECURITY_TOKEN")
    INSTANCE_URL = os.getenv("SALESFORCE_INSTANCE_URL")

class TwilioConfig:
    ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER") 

class DialogflowConfig:
    PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
    #GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")
    GOOGLE_LOCATION = os.getenv("REGION")
    GOOGLE_AGENT_ID = os.getenv("GOOGLE_AGENT_ID")
    API_ENDPOINT = f"{os.getenv("REGION")}-dialogflow.googleapis.com"