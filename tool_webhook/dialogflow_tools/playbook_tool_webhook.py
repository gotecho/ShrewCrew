from flask import Flask, request, jsonify
import requests
from . import arcgis_helpers as a
import sys
import os
from dotenv import load_dotenv
import traceback
import logging
from dialogflow_tools.scraper import scrape_city_data

app = Flask(__name__)

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


@app.route("/generic-case-post", methods=["POST"])
def push_to_salesforce_generic():
    """
    Receives case data from Dialogflow CX and pushes it to Salesforce.
    """
    try:
        token = getToken() 
        case_url = f"{url}/sobjects/Case"
        # Extract request JSON
        data = request.get_json()

        # Extract fields from request body
        first_name = str(data.get("firstName", "")).strip()
        last_name = str(data.get("lastName", "")).strip()
        phone = str(data.get("phone", "0")).strip()
        issue_type = str(data.get("issueType", "General Inquiry")).strip()
        description = data.get("description", "")
        address = data.get("address", "")

        # Validate required fields
        required_fields = [first_name, last_name, phone, issue_type, description, address]
        if not all(required_fields):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400

        # Validate input types
        if not isinstance(first_name, str) or not isinstance(last_name, str):
            return jsonify({
                "success": False,
                "error": "Invalid input type for name fields"
            }), 400

        if not isinstance(phone, str) or not phone.isdigit() or len(phone) != 10:
            return jsonify({
                "success": False,
                "error": "Invalid phone number"
            }), 400

        if not isinstance(description, str):
            return jsonify({
                "success": False,
                "error": "Invalid input type for description"
            }), 400

        if not isinstance(address, str):
            return jsonify({
                "success": False,
                "error": "Invalid input type for address"
            }), 400

        addr_resp = a.geocode(address, 90)["internal_geocoder"]

        if not addr_resp or not addr_resp.get("candidates"):
            return jsonify({
                "success": False,
                "error": "Address is outside the service area"
            }), 401

        # Determine if the case is anonymous
        is_anonymous = not first_name and not last_name

        # Construct Salesforce request payload
        case_payload = {
            "Subject": f"{issue_type} - {'Anonymous' if is_anonymous else f'''{first_name if first_name else ''} {last_name if last_name else ''}'''.strip()}",
            "Status": "New",
            "Description": description,
            "Origin": "Web",
            "Priority": "Medium",
            "SuppliedPhone": None if is_anonymous else phone,
        }

        # Add geocoded address fields if available
        if addr_resp and "candidates" in addr_resp and addr_resp["candidates"]:
            candidate = addr_resp["candidates"][0]  # Get the first result

            case_payload.update({
                "Address_Geolocation__Latitude__s": candidate.get("location", {}).get("y"),
                "Address_Geolocation__Longitude__s": candidate.get("location", {}).get("x"),
                "Address_X__c": candidate.get("attributes", {}).get("X"),
                "Address_Y__c": candidate.get("attributes", {}).get("Y"),
                "Address__c": candidate.get("address"),
                "GIS_City__c": candidate.get("attributes", {}).get("City"),
                "Street_Center_Line__c": candidate.get("attributes", {}).get("Loc_name"),
            })

        # Remove None values
        case_payload = {k: v for k, v in case_payload.items() if v is not None}

        # Send POST request to Salesforce
        response = requests.post(
            case_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=case_payload,
        )

        # Check response status
        if response.status_code in (200, 201, 204):
            return jsonify({
                "success": True,
                "salesforce_response": response.json()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": f"Salesforce API returned {response.status_code}",
                "details": response.text
            }), response.status_code

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"success": False, "error": "Server error", "details": str(e)}), 500


@app.route('/file-abandoned-vehicle', methods=['POST'])
def abandonedVehicle():
    try:
        token = getToken() 
        case_url = f"{url}/sobjects/Case"
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        data = request.get_json()
        make = data.get("make")
        model = data.get("model")
        color = data.get("vehicleColor")
        license = data.get("licensePlate")
        daysAbandoned = data.get("timePeriod")
        location = data.get("location")
        firstName = data.get("firstName")
        lastName = data.get("lastName")
        phoneNumber = data.get("phoneNumber")
        addr_resp = a.geocode(location, 90)["internal_geocoder"]

        if len(addr_resp) == 0:
            return jsonify({"Success": False, "Error": "Address is outside the service area"}), 401  

        case_data = {
            "Description": 
            f"""
                Vehicle: {color} {make} {model}
                License Plate: {license}
                Number of Days Abandoned: {daysAbandoned}
                Full Name (If Given): {firstName} {lastName}
                Phone Number (If Given): {phoneNumber}                
            """
        }

        if addr_resp and "candidates" in addr_resp and addr_resp["candidates"]:
            candidate = addr_resp["candidates"][0]  

        case_data.update({
            "Address_Geolocation__Latitude__s": candidate.get("location", {}).get("y"),
            "Address_Geolocation__Longitude__s": candidate.get("location", {}).get("x"),
            "Address_X__c": candidate.get("attributes", {}).get("X"),
            "Address_Y__c": candidate.get("attributes", {}).get("Y"),
            "Address__c": candidate.get("address"),
            "GIS_City__c": candidate.get("attributes", {}).get("City"),
            "Street_Center_Line__c": candidate.get("attributes", {}).get("Loc_name"),
         })

        case_response = requests.post(case_url, headers=headers, json=case_data)
        case_id = case_response.json().get("id")
        print(f"case data: {case_data}")
        print(f"case response: {case_response}")

        if case_response.status_code in (200, 201, 204):
            print(f"Case Id: {case_id}")
            return jsonify({"Success": True, "Case Id": case_id}), 200
        else:
            return jsonify({"Success": False, "Error": f"Salesforce returned with {case_response.status_code}"}), case_response.status_code
    
    except Exception as error:
        print(sys.exc_info())
        return jsonify({"Success": False, "Error": "Internal Server Error Occured"}), 500


@app.route('/dead_animal', methods=['POST'])
def deadAnimal():
    try:
        token = getToken()
        case_url = f"{url}/sobjects/Case"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        data = request.get_json()

        locationType = data.get("locationType")
        location = data.get("location")
        animalType = data.get("animalType")
        animalTotal = data.get("animalTotal")

        if locationType == "Right of Way": 
            chamActivityType = "DEAD ST"
            chamActivitySubType = "DEAD ST"
            chamPriority = 4
        elif locationType == "Private Property":
            chamActivityType = "DEAD PP"
            chamActivitySubType = "DEAD PP"
            chamPriority = 4

        firstName = data.get("firstName")
        lastName = data.get("lastName")
        phoneNumber = data.get("phoneNumber")
        addr_resp = a.geocode(location, 90)["internal_geocoder"]

        if len(addr_resp) == 0:
            return jsonify({"Success": False, "Error": "Address is outside the service area"}), 401  


        case_data = {
            "Description" : f" Location Type: {locationType}, Location: {location}, Animal Type: {animalType}, Animal Total: {animalTotal}, CHAMELEON Activity Type: {chamActivityType}, CHAMELEON Activity Sub Type: {chamActivitySubType}, CHAMELEON Priority: {chamPriority}, firstName: {firstName}, lastName: {lastName}, phonenumber: {phoneNumber}"
  
        }

        if addr_resp and "candidates" in addr_resp and addr_resp["candidates"]:
            candidate = addr_resp["candidates"][0]  

        case_data.update({
            "Address_Geolocation__Latitude__s": candidate.get("location", {}).get("y"),
            "Address_Geolocation__Longitude__s": candidate.get("location", {}).get("x"),
            "Address_X__c": candidate.get("attributes", {}).get("X"),
            "Address_Y__c": candidate.get("attributes", {}).get("Y"),
            "Address__c": candidate.get("address"),
            "GIS_City__c": candidate.get("attributes", {}).get("City"),
            "Street_Center_Line__c": candidate.get("attributes", {}).get("Loc_name"),
         })

        case_response = requests.post(case_url, headers=headers, json=case_data)
        case_id = case_response.json().get("id")

        if case_response.status_code in (200, 201, 204):
            print(f"Case Id: {case_id}")
            return jsonify({"Success": True, "Case Id": case_id}), 200
        else:
            return jsonify({"Success": False, "Error": f"Salesforce returned with {case_response.status_code}"}), case_response.status_code

    except Exception as error:
        print(sys.exc_info())
        return jsonify({"Success": False, "Error": "Internal Server Error Occurred."}), 500
    
    
@app.route("/311-data", methods=["POST"])
def scrape_and_return_data():
    try:
        user_query = request.json.get('userQuery', '')
        
        if not user_query:
            return jsonify({
                "success": False,
                "error": "Missing 'userQuery' in the request body"
            }), 400
        
        data = scrape_city_data(user_query)

        return jsonify(data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to scrape data",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
