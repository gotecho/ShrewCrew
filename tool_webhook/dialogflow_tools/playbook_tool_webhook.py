from flask import Flask, request, jsonify
import requests
from dialogflow_tools import arcgis_helpers as a
import sys
import os
from dotenv import load_dotenv
import traceback
from dialogflow_tools import scraper
import urllib.parse as urlp
from google.cloud import firestore
import datetime

app = Flask(__name__)

db = firestore.Client()

load_dotenv()

auth_url = os.getenv("SALESFORCE_AUTH_URL")
client_id = os.getenv("SALESFORCE_CLIENT_ID")
client_secret = os.getenv("SALESFORCE_SECRET_KEY")
username = os.getenv("SALESFORCE_USERNAME")
password = os.getenv("SALESFORCE_PASSWORD")
grant_type = "password"
url = os.getenv("SALESFORCE_URL")


def log_ticket_to_firestore(phone, case_id, issue_type, status="Open"):
    try:
        db.collection("tickets").add({
            "phone": phone,
            "issue_type": issue_type,
            "case_id": case_id,
            "status": status,
            "created_at": datetime.datetime.utcnow()
        })
        print(f" Logged to Firestore: {phone}")
    except Exception as e:
        print(f" Firestore logging failed: {e}")


def getToken():
    """ Function to regenerate and validate a new Salesforce token

    Raises:
        Exception: If the authentication for Salesforce fails, exception raised.

    Returns:
        String: String token for Salesforce authentication.
    """
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
    """ Function to take information from the DialogflowCX conversational agent and post it into Salesforce.

    Returns:
        JSON: Json containing a string to represent success or failure, and another string to
                represent the Salesforce ticket number.
    """
    try:
        token = getToken() 
        case_url = f"{url}/sobjects/Case"
        data = request.get_json()

        # Extract raw fields
        first_name_raw = data.get("firstName")
        last_name_raw = data.get("lastName")
        phone_raw = data.get("phone")
        issue_type_raw = data.get("issueType")
        description_raw = data.get("description")
        address_raw = data.get("address")

        # === Type Validation ===
        if first_name_raw is not None and not isinstance(first_name_raw, str):
            return jsonify({"success": False, "error": "Invalid input type for firstName"}), 400

        if last_name_raw is not None and not isinstance(last_name_raw, str):
            return jsonify({"success": False, "error": "Invalid input type for lastName"}), 400

        if phone_raw is not None and not isinstance(phone_raw, str):
            return jsonify({"success": False, "error": "Invalid input type for phone"}), 400

        if not isinstance(description_raw, str):
            return jsonify({"success": False, "error": "Invalid input type for description"}), 400

        if not isinstance(address_raw, str):
            return jsonify({"success": False, "error": "Invalid input type for address"}), 400

        # === Check for Missing Required Fields ===
        if any(field is None or not field.strip() for field in [issue_type_raw, description_raw, address_raw]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # === Safe Assignments After Validation ===
        first_name = (first_name_raw or "").strip()
        last_name = (last_name_raw or "").strip()
        phone = (phone_raw or "").strip()
        issue_type = (issue_type_raw or "General Inquiry").strip()
        description = description_raw.strip()
        address = address_raw.strip()

        # === Anonymous Check ===
        is_anonymous = not first_name and not last_name

        # === Phone Validation ===
        if not is_anonymous:
            if not phone.isdigit() or len(phone) != 10:
                return jsonify({"success": False, "error": "Invalid phone number"}), 400

        addr_resp = a.geocode(address, 90)["internal_geocoder"]

        if not addr_resp or not addr_resp.get("candidates"):
            return jsonify({
                "success": False,
                "error": "Address is outside the service area"
            }), 401

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
            case_id = response.json().get("id")

            log_ticket_to_firestore(phone, case_id, issue_type)

            return jsonify({
                "success": True,
                "salesforce_response": case_id
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
    """ Path used to file the case specific information gathered from Dialogflow CX about an abandoned
        vehicle.

    Returns:
        JSON: Json containing a string to represent success or failure, and another string to
                represent the Salesforce ticket number.
    """    
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
            return jsonify({"success": False, "error": "Address is outside the service area"}), 401  

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
        print("Salesforce response JSON:", case_response.json(), flush=True)
        case_id = case_response.json().get("id")
        print(f"case data: {case_data}")
        print(f"case response: {case_response}")

        if case_response.status_code in (200, 201, 204):
            issue_type = "Abandoned Vehicle"
            print(f"Case Id: {case_id}")
            log_ticket_to_firestore(phoneNumber, case_id, issue_type)
            return jsonify({"success": True, "caseId": case_id}), 200
        else:
            return jsonify({"success": False, "error": f"Salesforce returned with {case_response.status_code}"}), case_response.status_code
    
    except Exception as error:
        print(sys.exc_info())
        return jsonify({"success": False, "error": "Internal Server Error Occured"}), 500


@app.route('/dead_animal', methods=['POST'])
def deadAnimal():
    """ Path used to file the case specific information gathered from Dialogflow CX about a
        dead animal.

    Returns:
        JSON: Json containing a string to represent success or failure, and another string to
                represent the Salesforce ticket number.
    """
     
    try:
        token = getToken()
        case_url = f"{url}/sobjects/Case"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Missing or invalid JSON body"}), 400
        
        

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
            return jsonify({"success": False, "error": "Address is outside the service area"}), 401  

        case_data = {
            "Description" : 
            f""" 
                Location Type: {locationType}
                Location: {location}
                Animal Type: {animalType}
                Animal Total: {animalTotal}
                CHAMELEON Activity Type: {chamActivityType}
                CHAMELEON Activity Sub Type: {chamActivitySubType}
                CHAMELEON Priority: {chamPriority}
                firstName: {firstName}
                lastName: {lastName}
                phonenumber: {phoneNumber}
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


        print("Case data to Salesforce:", case_data)

       


        
        case_response = requests.post(case_url, headers=headers, json=case_data)
        print(f"Salesforce response status: {case_response.status_code}")
        print(f"Salesforce response body: {case_response.text}")
        

        if case_response.status_code in (200, 201, 204):
            case_id = case_response.json().get("id")
            issue_type = "Dead Animal"
            print(f"caseId: {case_id}")
            log_ticket_to_firestore(phoneNumber, case_id, issue_type)
            return jsonify({"success": True, "caseId": case_id}), 200
        else:
            print("Exception occurred:")
            print(f"Status Code: {case_response.status_code}, Response: {case_response.text}")
            return jsonify({"success": False, "error": f"Salesforce returned with {case_response.status_code}"}), case_response.status_code

    except Exception as e:
        print("Exception occurred:")
        print(traceback.format_exc())  # This shows the actual line that failed
        return jsonify({"success": False, "error": "Internal Server Error Occurred.", "details": str(e)}), 500

    
@app.route("/311-data", methods=["POST"])
def scrape_and_return_data():
    """ Takes the user query from Dialogflow CX and scrapes the websites for
        the City of Sacramento's services and returns the useful information.

    Returns:
        JSON: Returns a JSON containing the scraped information from the
              311 services links pertaining to the user. Or error if failed.
    """
    try:
        user_query = request.json.get('userQuery', '')
        
        if not user_query:
            return jsonify({
                "success": False,
                "error": "Missing 'userQuery' in the request body"
            }), 400
        
        data = scraper.scrape_city_data(user_query)

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
