from request_flow.services.dialogflow_service import detect_intent_text

if __name__ == "__main__":
    session_id = "connect-check-session"
    user_input = "Hi, I want to report illegal dumping."

    try:
        print("Sending to DialogFlow CX...")
        response = detect_intent_text(user_input, session_id)

        print("\n SUCCESS — DialogFlow CX responded!")
        print("Session ID:", session_id)
        print("Agent said:", response['queryResult']['responseMessages'][0]['text']['text'][0])

    except Exception as e:
        print("\n ERROR — DialogFlow CX connection failed:")
        print(str(e))