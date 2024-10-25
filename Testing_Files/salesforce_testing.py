#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv

load_dotenv() 
print(sys.path)
sys.path.append('/usr/local/lib/python3.11/site-packages')
import requests
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API")) 

auth_url = os.getenv("SALESFORCE_AUTH_URL")
client_id = os.getenv("SALESFORCE_CLIENT_ID")
client_secret = os.getenv("SALESFORCE_SECRET_KEY")
username = os.getenv("SALESFORCE_USERNAME")
password = os.getenv("SALESFORCE_PASSWORD")
grant_type = "password"

# Prepare the payload for the OAuth request
payload = {
    "grant_type": grant_type,
    "client_id": client_id,
    "client_secret": client_secret,
    "username": username,
    "password": password
}

# Make a POST request to get the access token
response = requests.post(auth_url, data=payload)

# Check if the request was successful
if response.status_code == 200:
    # Parse the access token from the response
    access_token = response.json().get("access_token")
    instance_url = response.json().get("instance_url")
    print(f"Access Token: {access_token}")
    print(f"Instance URL: {instance_url}")
else:
    print(f"Failed to retrieve access token. Status Code: {response.status_code}, Response: {response.text}")

# Set up the headers with the access token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

case_id = "5001t00001AbCdEF" # Replace with actual case numbers later to test

# Salesforce API endpoint for retrieving a case by its ID
case_url = f"{instance_url}/services/data/v52.0/sobjects/Case/{case_id}"

# Make the GET request to fetch the case details
response = requests.get(case_url, headers=headers)

model = genai.GenerativeModel('gemini-1.5-flash-latest') # Uses the gemini model we are working with.

response1 = model.generate_content(f"""Please relay the information from this json input {response.text} in
                                   a conversational manor.""")

print(response1.text)
print()

# Check if the request was successful
if response.status_code == 200:
    case_data = response.json()
    print(f"Case Data: {case_data}")
else:
    print(f"Failed to retrieve case. Status Code: {response.status_code}, Response: {response.text}")