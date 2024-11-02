# python 3.9+ required
import google.generativeai as genai #Make sure you have generative ai downloaded.
# Do pip3 install --upgrade google.generativeai
import requests # do pip install requests
from google.generativeai import generate_text
genai.configure(api_key="API_KEY") # Configures api key.

def generate_gemini_response(prompt):

    response = generate_text(
        model = 'gemini-1.5-flash-latest',
        prompt = prompt,
        temperature = 0.7,
        max_output_tokens = 100

    )
    return response.text
