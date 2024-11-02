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

# test data to post to database
my_data = {'Test Key': 'Test Value'}

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
    print(f"Access Token: {access_token}, URL: {instance_url}")
else:
    print("Couldn't get access token!")
    print(f"Error: {response.status_code}, {response.reason}")

# use access url to post data
response = requests.post(instance_url, json = my_data)

# if successful, print success
# else, print error
if response.status_code == 200:
    print("Success!")
    print(response.json)
else:
    print(f"Error: {response.status_code}, {response.reason}")
   
