from flask import Flask, request, jsonify
import requests
import arcgis_helpers as a
import sys
import os
from dotenv import load_dotenv
import traceback
import logging
from scraper import scrape_city_data

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


@app.route("/validate-address", methods=["POST"])
def validate():
    data = request.get_json()
    address = data.get("address", "").strip()
    cross_street = data.get("cross_street", "").strip()

    if not address and not cross_street:
        return jsonify({"valid": False, "message": "No address or street provided"}), 400

    if cross_street:
        # Construct full address using cross street
        full_address = f"{address} & {cross_street}, {'Sacramento'}"
    elif address and " " not in address:
        # If only a street name is given, add the default city
        full_address = f"{address}, {'Sacramento'}"
    else:
        full_address = address

    is_valid, message = a.geocode(full_address)
    return jsonify({"valid": is_valid, "message": message})

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
        response = requests.get("https://api64.ipify.org?format=json")
        public_ip = response.json()["ip"]

        print(f"Your public IP address is: {public_ip}")

        # Extract fields from request body
        first_name = str(data.get("firstName", "")).strip()
        last_name = str(data.get("lastName", "")).strip()
        phone = str(data.get("phone", "0")).strip()
        issue_type = str(data.get("issueType", "General Inquiry")).strip()
        description = str(data.get("description", "")).strip()
        address = str(data.get("address", "")).strip()
        addr_resp = a.geocode(address, 90)["internal_geocoder"]
    

        if len(addr_resp) == 0:
            return jsonify({
                "success": False,
                "error": "Address is outside the service area",
                "details": "The provided address is not within the supported region."
            }), 401  # Return 401 Bad Request out of sacramento

        # Determine if the case is anonymous
        is_anonymous = not first_name and not last_name

        # Construct Salesforce request payload
        case_payload = {
            "Subject": f"{issue_type} - {'Anonymous' if is_anonymous else f'''{first_name if first_name else ''} {last_name if last_name else ''}'''.strip()}",
            "Status": "New",
            "Description": description,
            "Origin": "Web",
            "Priority": "Medium",
            "ContactMobile": None if is_anonymous else phone,
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
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",}

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

        case_data = {
            "Description": 
            f"""
                Vehicle: {color} {make} {model}
                License Plate: {license}
                Location: {location}
                Number of Days Abandoned: {daysAbandoned}
                Full Name (If Given): {firstName} {lastName}
                Phone Number (If Given): {phoneNumber}                
            """
        }

        case_response = requests.post(case_url, headers=headers, json=case_data)
        case_id = case_response.json().get("id")

        return jsonify({"Success": True, "Case Id": case_id}), 200
    
    except Exception as error:
        return jsonify({"Success": False, "Error": str(error)}), 500


@app.route('/dead_animal', methods=['POST'])
def deadAnimal():
    try:
        token = getToken()
        case_url = f"{url}/sobjects/Case"
        headers = {"Authorization": f"Bearer {token}"}

        data = request.get_json()

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

        firstName = data.get("firstName")
        lastName = data.get("lastName")
        phoneNumber = data.get("phoneNumber")


        case_data = {
            "Description" : f"Animal Location: {location}, Animal Type: {animalType}, Animal Total: {animalTotal}, CHAMELEON Activity Type: {chamActivityType}, CHAMELEON Activity Sub Type: {chamActivitySubType}, CHAMELEON Priority: {chamPriority}, firstName: {firstName}, lastName: {lastName}, phonenumber: {phoneNumber}"
  
        }
        case_response = requests.post(case_url, headers=headers, json=case_data)
        case_id = case_response.json().get("id")
        return jsonify({"Success": True, "Case Id": case_id.json})
    except Exception as error:
        return jsonify({"Success": False, "Error": str(error)}), 500
    
    
@app.route("/311-data", methods=["POST"])
def scrape_and_return_data():
    try:
        user_query = request.json.get('userQuery', '')
        
        if not user_query:
            return jsonify({
                "success": False,
                "error": "Missing 'userQuery' in the request body"
            }), 400
        
        # Scrape data based on the query
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
