import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# Firestore Database Setup
database = firestore.Client()

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

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
    LOCATION = os.getenv("GOOGLE_LOCATION")
    AGENT_ID = os.getenv("GOOGLE_AGENT_ID")
    CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
    API_ENDPOINT = f"{LOCATION}-dialogflow.googleapis.com"