import os
from google.oauth2 import service_account
from google.cloud import dialogflowcx_v3
from config import Config

DIALOGFLOW_ENDPOINT = f"{Config.GOOGLE_LOCATION}-dialogflow.googleapis.com"

credentials = service_account.Credentials.from_service_account_file(Config.GOOGLE_CREDENTIALS_PATH)
client_options = {"api_endpoint": DIALOGFLOW_ENDPOINT}
client = dialogflowcx_v3.SessionsClient(credentials=credentials, client_options=client_options)


def detect_intent_text(text, session_id="123456"):
    
    session_path = client.session_path(
        Config.GOOGLE_PROJECT_ID,
        Config.GOOGLE_LOCATION,
        Config.GOOGLE_AGENT_ID,
        session_id
    )

    text_input = dialogflowcx_v3.TextInput(text=text)
    query_input = dialogflowcx_v3.QueryInput(text=text_input, language_code="en")

    request = dialogflowcx_v3.DetectIntentRequest(
        session=session_path, 
        query_input=query_input)

    response = client.detect_intent(request=request)

    if response.query_result.response_messages:
        return response.query_result.response_messages[0].text.text[0]
    else:
        return "No response from Dialogflow."