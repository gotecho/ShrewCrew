#!/usr/bin/env python3
import sys
import os
print(sys.path)
sys.path.append('/usr/local/lib/python3.11/site-packages')
import requests

auth_url = "https://test.salesforce.com/services/oauth2/token"
client_id = "3MVG9RHx1QGZ7OsglF7bGHgSAlMfHROUlnMxburNqgasDSWaXsgx4bRDY0alceJEWveBR2LtxfqlFsRUb5deH"
client_secret = "SUPER SECRET KEY TO BE REPLACED EACH TIME"
username = "apiuser@cityofsacramento.org.qa"
password = "SUPER SECRET PASSWORD TO BE REPLACED EACH TIME"
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

# Check if the request was successful
if response.status_code == 200:
    case_data = response.json()
    print(f"Case Data: {case_data}")
else:
    print(f"Failed to retrieve case. Status Code: {response.status_code}, Response: {response.text}")