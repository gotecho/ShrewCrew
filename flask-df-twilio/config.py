import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
    GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION")
    GOOGLE_AGENT_ID = os.getenv("GOOGLE_AGENT_ID")
    GOOGLE_CREDENTIALS_PATH = os.path.join(BASE_DIR, "twiliosacstate-3cdfaefd910c.json")

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")