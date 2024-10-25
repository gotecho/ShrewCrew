# python 3.9+ required
import google.generativeai as genai #Make sure you have generative ai downloaded.
# Do pip3 install --upgrade google.generativeaih
import requests # do pip install requests

genai.configure(api_key="API_KEY") # Configures api key.

model = genai.GenerativeModel('gemini-1.5-flash-latest') # Uses the gemini model we are working with.

user_prompt = input("Please enter your prompt: ")  # Prompt the user for input using the keyboard

response = model.generate_content(user_prompt)  # Sends the user-provided prompt to the AI.

print(response.text)  # AI generates a response and is stored in response as text.