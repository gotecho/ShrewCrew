import os
from google.oauth2 import service_account
from google.cloud import dialogflowcx_v3


from config import Config

# Define the correct regional endpoint
DIALOGFLOW_ENDPOINT = f"{Config.GOOGLE_LOCATION}-dialogflow.googleapis.com"

#  Create the client with the correct endpoint
credentials = service_account.Credentials.from_service_account_file(Config.GOOGLE_CREDENTIALS_PATH)
client_options = {"api_endpoint": DIALOGFLOW_ENDPOINT}
client = dialogflowcx_v3.SessionsClient(credentials=credentials, client_options=client_options)

def detect_intent_text(text, session_id="123456"):
    """Sends user input to Dialogflow CX and gets response."""

    # Generate the correct session path using client methods
    session_path = client.session_path(
        Config.GOOGLE_PROJECT_ID,
        Config.GOOGLE_LOCATION,
        Config.GOOGLE_AGENT_ID,
        session_id
    )

    # Prepare text input
    text_input = dialogflowcx_v3.TextInput(text=text)
    query_input = dialogflowcx_v3.QueryInput(text=text_input, language_code="en")

    # Create the DetectIntentRequest object
    request = dialogflowcx_v3.DetectIntentRequest(
        session=session_path,
        query_input=query_input
    )

    # Make API call to Dialogflow CX
    response = client.detect_intent(request=request)

    # Handle response safely
    if response.query_result.response_messages:
        return response.query_result.response_messages[0].text.text[0]
    else:
        return "No response from Dialogflow."
