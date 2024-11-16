import sys
import requests
import os
from dotenv import load_dotenv


# TODO: Add code that tries to get posted data to see if it really is in
# database


# load env enviornments 
load_dotenv() 
# init variables for authentication 
auth_url = os.getenv("SALESFORCE_AUTH_URL")
client_id = os.getenv("SALESFORCE_CLIENT_ID")
client_secret = os.getenv("SALESFORCE_SECRET_KEY")
username = os.getenv("SALESFORCE_USERNAME")
password = os.getenv("SALESFORCE_PASSWORD")
grant_type = "password"
url = os.getenv("SALESFORCE_URL")


# create a dictionary to store authentication variables
authenticate = {
    "grant_type": grant_type,
    "client_id": client_id,
    "client_secret": client_secret,
    "username": username,
    "password": password
}

# post authentication to url to get access to the database
response = requests.post(auth_url, data=authenticate)

# if successful, store access token and url in variables
# else, print error
if response.status_code == 200:
    access_token = response.json().get("access_token")
    instance_url = response.json().get("instance_url")
    print(f"Access Token: {access_token}, Instance URL: {instance_url}, URL from ENV: {url}")
else:
    print("Couldn't get access token!")
    print(f"Error: {response.status_code}, {response.reason}")

case_data = {
    'Name' : 'John Doe',
    'Description' : 'This is a test case',
    'Phone Number' : '123-456-789'
}
   

case_url = f"{url}/sobjects/Case"

headers={"Authorization": f"Bearer {access_token}"}


case_response = requests.post(case_url, headers, json=case_data)

if case_response.status_code not in (200, 201, 204):
    print("Couldn't create test case!")
    print(f"Error: {case_response.status_code}, {case_response.reason}")
else:
    case_id = case_response.json().get("id")
    print(f"Case id: {case_id}")

