# python 3.9+ required
import google.generativeai as genai #Make sure you have generative ai downloaded.
# Do pip3 install --upgrade google.generativeai
import requests # do pip install requests
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
            model = genai.GenerativeModel("gemini-1.5-flash") 
            response = model.generate_content(prompt)

            if response.candidates and len(response.candidates) > 0:
                return response.candidates[0].content.parts[0].text

            return "No candidates found."

        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error generating response."
