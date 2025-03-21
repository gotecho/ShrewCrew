from datetime import datetime
import requests
import os
from operator import itemgetter
from dotenv import load_dotenv


load_dotenv()

def geocode(address: str, threshold=80, salesforce_case_object=None) -> dict[str, dict]:
    """
    Function to validate an address string though both world geocoder and City's internal geocoder
        address <string>: address string
        threshold <int>: threshold for the  address match
    returns:
        <dict> : dictionary with output from world geocoder and cities internal geocoder
    """

    def _find_candidate(json_input, threshold=85):
        """
        Function to get the best address match from the given json response from
        geocoder response paramaters. Gets the candidate with greatest score or
        if multiple candidates have the same greatest score pick the first
        occurence where City == "Sacramento" If no occurences of City ==
        "Sacramento", returns the first candidate in the list.
        """

        out = {"spatialReference": json_input["spatialReference"]}
        score = threshold

        if "candidates" not in json_input.keys() or len(json_input["candidates"]) == 0:
            return []


        response = requests.get("https://api64.ipify.org?format=json")
        public_ip = response.json()["ip"]

        print(f"Your public IP address is: {public_ip}")
   
        # Get candidate with greatest score or if multiple candidates have the same greatest score pick the first occurence where City == "Sacramento"
        # If no occurences of City == "Sacramento", return the first candidate in the list
        candidate_list = [(index, candidate) for (index, candidate) in enumerate(json_input["candidates"]) if candidate["score"] >= score]
        
        if not candidate_list:
            return []
        
        scores = [(index, candidate["score"]) for (index, candidate) in candidate_list]
        max_scores = [t for t in scores if t[1] == max(scores, key=itemgetter(1))[1]]
        
        if len(max_scores) > 1:
            for (index, score) in max_scores:
                candidate = candidate_list[index][1]
                if candidate.get('attributes').get('City').lower() == "sacramento":
                    out.update({"candidates": [candidate_list[index][1]]})
                    return out
        
        if not candidate_list[0][1].get('address'):
            return []    
        
        out.update({"candidates": [candidate_list[0][1]]})
        return out

    original_address = address.replace(" USA", "")

    url = os.getenv("WORLD_GEOCODER_URL")
    params = {
        "SingleLine": original_address,
        "outFields": "*",
        "f": "pjson",
        "maxLocations": 10,
    }

    start = datetime.now()

    world_response = requests.get(url, params=params)

    duration = round((datetime.now() - start).microseconds / 1000)


    world_candidate = _find_candidate(world_response.json(), threshold=threshold)

    internal_candidate = []
    overview = []

    if not isinstance(threshold, int):
        threshold = int(threshold)

    # If score >= 80, resulting address is passed to internal geocoder
    # Else, pass the original user-given address to the internal geocoder instead
    if (
        world_response.status_code == 200
        and isinstance(world_candidate, dict)
        and "candidates" in world_candidate.keys()
        and len(world_candidate["candidates"]) > 0
        and world_candidate["candidates"][0]["score"] >= threshold
    ):
        address = world_candidate["candidates"][0]["attributes"]["ShortLabel"]
        street = world_candidate["candidates"][0]["attributes"]["StAddr"]
        city = world_candidate["candidates"][0]["attributes"]["City"]
        county = world_candidate["candidates"][0]["attributes"]["Subregion"]
        zip_code = world_candidate["candidates"][0]["attributes"]["Postal"]

        city_geocoder_url = (os.getenv("EXTERNAL_GIS_URL") + "ADDRESS_AND_STREETS/GeocodeServer/findAddressCandidates?")
        params = {
            "Street": street,
            "City": city,
            "ZIP": zip_code,
            "SingleLine": address,
            "outFields": "*",
            "outSR": "4326",
            "maxLocations": 10,
            "f": "pjson",
        }

        start = datetime.now()

        city_response = requests.get(url=city_geocoder_url, params=params)
        print(f"Response Status Code: {city_response.status_code}")
        print(f"Response Headers: {city_response.headers}")
        print(f"Response Text: {city_response.text}")
        
        duration = round((datetime.now() - start).microseconds / 1000)
        
        body = city_response.get_json()
        
        if ("candidates" in body and len(body["candidates"]) > 0):
            internal_candidate = _find_candidate(json_input=body, threshold=threshold)

        overview = {"address": address, "city": city, "county": county}

    else:
        city_geocoder_url = (os.getenv("EXTERNAL_GIS_URL") + "ADDRESS_AND_STREETS/GeocodeServer/findAddressCandidates?")
        params = {
            "SingleLine": address,
            "outFields": "*",
            "outSR": "4326",
            "maxLocations": 10,
            "f": "pjson",
        }

        start = datetime.now()

        city_response = requests.get(city_geocoder_url, params=params)
        
        duration = round((datetime.now() - start).microseconds / 1000)
        
        body = city_response.json()
        
        if ("candidates" in body and len(body["candidates"]) > 0):
            internal_candidate = _find_candidate(json_input=body, threshold=threshold)
            

    return {
        "world_geocoder": world_candidate,
        "internal_geocoder": internal_candidate,
        "overview": overview,
    }



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