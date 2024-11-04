from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API'))  # Store your API key in .env

def generate_gemini_response(prompt: str) -> str:
    """
    Function to generate a response from Google Gemini using GenerativeModel.
    prompt <string>: the prompt to send to Gemini
    returns:
        <string>: the response text from Gemini
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") 
        
        response = model.generate_content(prompt)

        if response.candidates and len(response.candidates) > 0:
            return response.candidates[0].content.parts[0].text

        return "No candidates found."

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error generating response."

def geocode(address: str, threshold=80) -> dict[str, dict]:
    """
    Function to validate if an address is in Sacramento, or return the closest address if not.
        address <string>: address string
        threshold <int>: threshold for the address match
    returns:
        <dict> : dictionary with a boolean indicating if address is in Sacramento and the matching address JSON if found,
                 or the closest match if Sacramento is not found
    """
    
    def _find_best_candidate(json_input, threshold=85):
        """
        Function to find the best match where City == "Sacramento" from the given json response.
        If no Sacramento address is found, returns the highest-scoring candidate.
        """
        if "candidates" not in json_input or not json_input["candidates"]:
            return None

        # Filter for candidates that meet the score threshold
        candidates = [candidate for candidate in json_input["candidates"] if candidate["score"] >= threshold]
        
        # Check for Sacramento candidate, return if found
        for candidate in candidates:
            if candidate.get("attributes", {}).get("City", "").lower() == "sacramento":
                return candidate, True
        
        # If no Sacramento candidate, return the highest-scoring candidate
        if candidates:
            best_candidate = max(candidates, key=lambda c: c["score"])
            return best_candidate, False
        
        return None, False
    
    if not address:
        raise ValueError('Required function parameter "address" is not defined.')

    original_address = address.replace(" USA", "")

    # World Geocoder request
    world_geocoder_url = os.environ.get("WORLD_GEOCODER_URL")
    params = {
        "SingleLine": original_address,
        "outFields": "*",
        "f": "pjson",
        "maxLocations": 10,
    }

    world_response = requests.get(world_geocoder_url, params=params)
    if world_response.status_code != 200:
        raise Exception("Error from world geocoder server")

    world_data = world_response.json()
    best_candidate, is_sacramento = _find_best_candidate(world_data, threshold=threshold)

        
    if best_candidate:
        gemini_prompt = f"{best_candidate['address']}. Is this a valid location in Sacramento? "
    else:
        gemini_prompt = f"The address {address} could not be matched. What could be a valid nearby location? "

    
    gemini_response = generate_gemini_response(gemini_prompt)

    # Return dict indicating if Sacramento candidate is found or the closest address otherwise
    return {"is_sacramento": is_sacramento, "address_data": best_candidate['address'],"gemini_response": gemini_response}


if __name__ == "__main__":
    addresses = ['1029 Betsy Ross Dr', "J street", 'foothills blvd']
    for address in addresses:
        result = geocode(address)
        print(f"Address: {address}")
        if result['address_data'] is None:
            print("No valid address found.")
        else:
            print(f"Is Sacramento: {result['is_sacramento']}")
            print(f"Matched Address: {result['address_data']}")
        
        print(f"Gemini Response: {result['gemini_response']}")
        print("")