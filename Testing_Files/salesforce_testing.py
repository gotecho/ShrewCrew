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
url = os.getenv("SALESFORCE_URL")

# Prepare the payload for the OAuth request
def auth_salesforce(): # authenticate salesforce
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
        return access_token, instance_url
    else:
        print(f"Failed to retrieve access token. Status Code: {response.status_code}, Response: {response.text}")
        return None, None

def get_salesforce_case_data(case_id):
# Set up the headers with the access token
    access_token, instance_url = auth_salesforce()

    if access_token and instance_url:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }


    # Salesforce API endpoint for retrieving a case by its ID
        case_url = f"{instance_url}/services/data/v52.0/sobjects/Case/{case_id}"

    # Make the GET request to fetch the case details
        response = requests.get(case_url, headers=headers)
# Checking if request is successful before giving it to gemini
    if response.status_code == 200:
        print(response.text)
        return response.json

    else:
        print(f"Failed to retrieve case. Status Code: {response.status_code}, Response: {response.text}")
        return None
    return None

get_salesforce_case_data('500WL00000AHk0fYAD')