# python 3.9+ required
import google.generativeai as genai #Make sure you have generative ai downloaded.
# Do pip3 install --upgrade google.generativeai

genai.configure(api_key="AIzaSyBUKLB2f4yuLoNxx4WUmYs1tGZWj-NUqdY") # Configures api key.

model = genai.GenerativeModel('gemini-1.5-flash-latest') # Uses the gemini model we are working with.

response = model.generate_content("Explain how a computer works to a child.") # sends a prompt to the AI.

print(response.text) # AI generates a response and is stored in response as text. 