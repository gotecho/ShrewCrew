def detect_intent_text(session_id, text, language_code="en"):
    from google.cloud import dialogflowcx_v3beta1 as dialogflow
    from project_structure.config import get_project_id, get_region, get_agent_id

    client = dialogflow.SessionsClient()
    session = client.session_path(
        project=get_project_id(),
        location=get_region(),
        agent=get_agent_id(),
        session=session_id,
    )

    text_input = dialogflow.TextInput(text=text)
    query_input = dialogflow.QueryInput(text=text_input, language_code=language_code)
    response = client.detect_intent(session=session, query_input=query_input)

    return response.query_result

