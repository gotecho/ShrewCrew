import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# Firestore Database Setup
database = firestore.Client(database="shrewcrew-database")

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")

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
    PROJECT_ID = os.getenv("PROJECT_ID")
    LOCATION = os.getenv("GOOGLE_LOCATION")
    GOOGLE_AGENT_ID = os.getenv("GOOGLE_AGENT_ID")
    API_ENDPOINT = f"{LOCATION}-dialogflow.googleapis.com"