import logging
from google.cloud import dialogflowcx_v3
from config import DialogflowConfig, Config
from google.auth import default



DIALOGFLOW_ENDPOINT = f"{Config.GOOGLE_LOCATION}-dialogflow.googleapis.com"

# Use ADC (gcloud auth application-default login)
credentials, _ = default()  
client_options = {"api_endpoint": f"{Config.GOOGLE_LOCATION}-dialogflow.googleapis.com"}
client = dialogflowcx_v3.SessionsClient(credentials=credentials, client_options=client_options)

def detect_intent_text(text, session_id="123456"):
    try:
        logging.info('Entering dialogflow_cx function')

        session_path = client.session_path(
            DialogflowConfig.PROJECT_ID,
            Config.GOOGLE_LOCATION,
            DialogflowConfig.GOOGLE_AGENT_ID,
            session_id
        )

        text_input = dialogflowcx_v3.TextInput(text=text)
        query_input = dialogflowcx_v3.QueryInput(text=text_input, language_code="en")

        request = dialogflowcx_v3.DetectIntentRequest(
            session=session_path,
            query_input=query_input
        )

        response = client.detect_intent(request=request)

        if response.query_result.response_messages:
            return response.query_result.response_messages[0].text.text[0]
        else:
            return "No response from Dialogflow."

    except Exception as e:
        logging.exception('Error in dialogflow_cx function')
        raise