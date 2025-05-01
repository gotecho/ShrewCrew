import os
import logging
from google.oauth2 import service_account
from google.cloud import dialogflowcx_v3

from config import Config

# Define the correct regional endpoint
DIALOGFLOW_ENDPOINT = f"{Config.GOOGLE_LOCATION}-dialogflow.googleapis.com"

# Use a function to load credentials and create the client on demand
def get_dialogflow_client():
    credentials = service_account.Credentials.from_service_account_file(Config.GOOGLE_CREDENTIALS_PATH)
    client_options = {"api_endpoint": DIALOGFLOW_ENDPOINT}
    return dialogflowcx_v3.SessionsClient(credentials=credentials, client_options=client_options)

def detect_intent_text(text, session_id):
    if not text:
        return "No response from Dialogflow."
    try:
        logging.info('Entering dialogflow_cx function')

        session_path = get_dialogflow_client().session_path(
            Config.GOOGLE_PROJECT_ID,
            Config.GOOGLE_LOCATION,
            Config.GOOGLE_AGENT_ID,
            session_id
        )

        text_input = dialogflowcx_v3.TextInput(text=text)
        query_input = dialogflowcx_v3.QueryInput(text=text_input, language_code="en")

        request = dialogflowcx_v3.DetectIntentRequest(
            session=session_path,
            query_input=query_input
        )

        response = get_dialogflow_client().detect_intent(request=request)

        if response.query_result.response_messages:
            texts = response.query_result.response_messages[0].text.text
            if texts:
                return texts[0]

        return "No response from Dialogflow."

    except Exception as e:
        logging.exception('Error in dialogflow_cx function')
        raise


