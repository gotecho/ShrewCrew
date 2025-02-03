# python 3.9+ required
import google.generativeai as genai #Make sure you have generative ai downloaded.
# Do pip3 install --upgrade google.generativeai
import requests # do pip install requests
import salesforce_testing
import json
import time
import os
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API")) # Configures api key.

# Define the required information for filing a ticket
ticket_requirements = {
    "make_model": None,
    "color": None,
    "street_name": None
}

# Check if all required fields are filled
def all_requirements_filled():
    return all(value is not None for value in ticket_requirements.values())

def initialize_chat_session():
    """Starts a Gemini chat session."""
    model = genai.GenerativeModel("gemini-pro")
    return model.start_chat()

chat_session = initialize_chat_session()

def collect_ticket_info():
    """Dynamically collects missing ticket information."""
    global chat_session

    while not all_requirements_filled():
        missing_fields = [key for key, value in ticket_requirements.items() if value is None]
        missing_prompt = f"I need more details to file your report. Missing: {', '.join(missing_fields)}."

        # Ask Gemini how to phrase the request
        gemini_prompt = f"{missing_prompt} Please ask the user only for the missing details in a friendly way."

        response = chat_session.send_message(gemini_prompt)
        print(f"Gemini: {response.text}")

        # Get user input
        user_input = input("Your response: ")

        # Match input to fields
        matched_response = match_user_input_to_field(user_input)

        # Process Gemini's response and update ticket fields
        for line in matched_response.split("\n"):
            if ": " in line:
                field, value = line.split(": ", 1)
                field = field.strip().lower().replace(" ", "_")  # Normalize field names

                if field in ticket_requirements and not ticket_requirements[field]:  
                    ticket_requirements[field] = value.strip()
                    print(f"Updated {field}: {value.strip()}")

        time.sleep(1)  # Prevent rapid looping

    print("All required details are collected.")

def retrieve_ticket_info():
    """Returns the collected ticket information as JSON."""
    if not all_requirements_filled():
        return {"error": "Not all required information is provided."}

    return json.dumps(ticket_requirements, indent=4)

def match_user_input_to_field(user_input):
    """Uses Gemini to determine which field the user's input corresponds to."""
    global chat_session

    # Provide the current known values to Gemini
    known_values = "\n".join([f"{k}: {v}" for k, v in ticket_requirements.items() if v])
    
    # Construct the prompt
    prompt = f"""
    The user is providing details for an abandoned vehicle report. 
    Here is what we already know:
    {known_values}

    The missing fields are: {', '.join([key for key, value in ticket_requirements.items() if value is None])}.
    
    Given this context, match the following user input to the appropriate field(s): "{user_input}".
    If the input contains information for multiple fields, extract and assign them accordingly.
    Return your response in the format: 'Field: Value'.
    """

    # Get Gemini's interpretation
    response = chat_session.send_message(prompt)
    return response.text

# Start data collection
collect_ticket_info()
ticket_data = retrieve_ticket_info()
print("Final Ticket Data:", ticket_data)