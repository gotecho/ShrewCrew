# python 3.9+ required
import google.generativeai as genai #Make sure you have generative ai downloaded.
# Do pip3 install --upgrade google.generativeai
import requests # do pip install requests
import salesforce_testing
import os
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API")) # Configures api key.


def generate_gemini_response(prompt: str) -> str:
        """
        Helper method to generate a response from Google Gemini using GenerativeModel.
        prompt <string>: the prompt to send to Gemini
        returns:
            <string>: the response text from Gemini
        """
        try:
            model = genai.GenerativeModel("gemini-pro") 
            response = model.generate_content(prompt)

            if response.candidates and len(response.candidates) > 0:
                return response.candidates[0].content.parts[0].text

            return "No candidates found."

        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error generating response."
        
        
def generate_case_prompt(case_data):
    """ Generate a prompt based on case data to ask the user of the required fields
    """

    case_type = case_data.get('Type')
    # required_fields = CASE_TYPE_FIELDS.get(case_type, []) For later
    # if not required_fields:
         #return "No required fields for this case" for now

    case_info = f"""
    Here is the case info:
    Case Number: {case_data.get('CaseNumber')}
    Subject: {case_data.get('Subject')}
    Status: {case_data.get('Status')}
    Priority: {case_data.get('Priority')}
    Created Date: {case_data.get('CreatedDate')}
    Owner: {case_data.get('Owner', {}).get('Name', 'N/A')}
    """

    #prompt = f"""
    #Based on the case information above, could you ask the user the following questions to fill in the missing fields or clarify details?
    #{case_info}
    #Required Fields: {', '.join(required_fields)}
    #Please ensure to phrase the questions clearly and guide the user on what needs to be updated or confirmed for these fields
    #""" 
    #return prompt

def gather_user_input(fields):
     """
     Simulate gathering user inputs for the missing or required fields
     """
     user_answers = {}
     for field in fields:
          user_answers[field] = input(f"Please provide the value for {field}: ")
          return user_answers
     
def main():
    case_id = "5001t00001AbCdEF"  # Example case ID, replace with actual ID
    case_data = salesforce_testing.get_salesforce_case_data(case_id)

    if case_data:
         prompt = generate_case_prompt(case_data)

         user_questions = generate_gemini_response(prompt)
         print("/nGemini's Questions for the User:")
         print(user_questions)

         #required_fields = CASE_TYPE_FIELDS.get(case_data.get('Type', 'Dead'), [])  # Default to 'Dead' if no type is found
         #user_answers = gather_user_inputs(required_fields)

         print("/nUser responses collected:")
         #print(user_answers)
    else:
         print("Unable to process case data.")

if __name__ == "__main__":
     main()