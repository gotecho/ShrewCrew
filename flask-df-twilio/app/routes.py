from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.dialogflow_cx import detect_intent_text
import sys
import requests
import os
from dotenv import load_dotenv

load_dotenv()

auth_url = os.getenv("SALESFORCE_AUTH_URL")
client_id = os.getenv("SALESFORCE_CLIENT_ID")
client_secret = os.getenv("SALESFORCE_SECRET_KEY")
username = os.getenv("SALESFORCE_USERNAME")
password = os.getenv("SALESFORCE_PASSWORD")
grant_type = "password"
url = os.getenv("SALESFORCE_URL")


def getToken():
    authenticate = {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }
    response = requests.post(auth_url, data=authenticate)
    response_data = response.json()

    if "access_token" in response_data:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise Exception(f"Failed to get access token from SalesForce: {response_data}")

        


main = Blueprint('main', __name__)

@main.route('/sms', methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body')
    sender_number = request.form.get('From')

    if not incoming_msg:
        return jsonify({"error": "No message received"}), 400

    # Send message to Dialogflow CX
    dialogflow_response = detect_intent_text(incoming_msg)

    # Prepare Twilio response
    twilio_response = MessagingResponse()
    twilio_response.message(dialogflow_response)

    return str(twilio_response)


@main.route('/file-abandoned-vehicle', methods=['POST'])
def abandonedVehicle():
    try:
        token = getToken() 
        case_url = f"{url}/sobjects/Case"
        headers={"Authorization": f"Bearer {token}"}

        data = request.json
        make = data.get("make")
        model = data.get("model")
        color = data.get("vehicleColor")
        license = data.get("licensePlate")
        daysAbandoned = data.get("timePeriod")

        case_data = {
            "Description" : {
                "Vehicle Make": make,
                "Vehicle Model": model,
                "Vehicle Color": color,
                "License Plate Number": license,
                "# of Days Abandoned": daysAbandoned
            }
        }

        case_response = requests.post(case_url, headers=headers, json=case_data)
        return jsonify({"Success": True, "SalesForce Response": case_response.json()})
    
    except Exception as error:
        return jsonify({"Success": False, "Error": str(error)}), 500


@main.route('/dead_animal', methods=['POST'])
def deadAnimal():
    try:
        token = getToken()
        case_url = f"{url}/sobjects/Case"
        headers = {"Authorization": f"Bearer {token}"}

        data = request.json

        location = data.get("location")
        animalType = data.get("animalType")
        animalTotal = data.get("animalTotal")

        if location == "Right of Way": 
            chamActivityType = "DEAD ST"
            chamActivitySubType = "DEAD ST"
            chamPriority = 4
        elif location == "Private Property":
            chamActivityType = "DEAD PP"
            chamActivitySubType = "DEAD PP"
            chamPriority = 4

        


        case_data = {
            "Description" : {
                "Animal Location": location,
                "Animal Type": animalType,
                "Animal Total": animalTotal,
                "CHAMELEON Activity Type": chamActivityType,
                "CHAMELEON Activity Sub Type": chamActivitySubType,
                "CHAMELEON Priority": chamPriority

            }
        }
        case_response = request.post(case_url, headers=headers, json=case_data)
        return jsonify({"Success": True, "SalesForce Response": case_response.json})
    except Exception as error:
        return jsonify({"Success": False, "Error": str(error)}), 500

