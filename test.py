from openai import OpenAI
from flask import Flask, render_template, request
import googlemaps
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
with open("promp.txt") as file:
    prompt = file.read()



def get_response(city, zip):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    ).choices[0].message.content





def get_zip_code(address):
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": os.getenv("GOOGLE_API_KEY")
    }
    
    response = requests.get(geocoding_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            for component in data["results"][0]["address_components"]:
                if "postal_code" in component["types"]:
                    return component["long_name"]  # Return the ZIP code
    return None  # Return None if ZIP code is not found


# if __name__ == "__main__":
#     pass
#     response = get_response('el paso', '79925')
#     response = response.strip("```").strip("json")
#     parsed_json = json.loads(response)

#     with open("generated_locations.json", "w") as file:
#          json.dump(parsed_json, file, indent=4)

#     for place in parsed_json:
#         print(place.get("address"))
    

#     valid_addresses = []
#     for place in parsed_json:
#         zip_code = get_zip_code(place.get("address"))
#         if zip_code == "79925":
#             print(f"Address '{place.get("name")}' is valid with ZIP code: {zip_code}")
#             valid_addresses.append(place)

#     print(json.dumps(valid_addresses, indent=4))


# Initialize the Google Maps client
API_KEY = "AIzaSyDeGVAtVn6hgsV9q4gNyBWHEEr9rgIDiNE"
gmaps = googlemaps.Client(key=API_KEY)

def get_coordinates(state, city, zip_code):
    """
    Get latitude and longitude for a given state, city, and zip code.
    """
    address = f"{city}, {state}, {zip_code}"
    geocode_result = gmaps.geocode(address)
    
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise ValueError("Unable to find coordinates for the given address.")

def get_zip_code_from_place(place):
    """
    Extract the ZIP code from a place's address using the Geocoding API.
    """
    place_address = place.get('vicinity', '')
    geocode_result = gmaps.geocode(place_address)
    #print(geocode_result[0]['address_components'])
    if geocode_result:
        for component in geocode_result[0]['address_components']:
            if 'postal_code' in component['types']:
                print(component['long_name'])
                return component['long_name']
    return None

def get_infrastructures_in_zip(lat, lng, zip_code, radius=100_000, max_results=50):
    """
    Get infrastructures (places of interest) near given coordinates, filtered by a specific ZIP code.
    """
    places_result = gmaps.places_nearby(
    location=(lat, lng),
    type="point_of_interest"
    )
    
    locations = []
    for place in places_result.get('results', []):
        #print(place.get('name'), place.get('postal_code'))
        # Check if the place is in the given ZIP code
        place_zip = get_zip_code_from_place(place)
        if place_zip == zip_code:
            locations.append({
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
            })
            if len(locations) >= max_results:
                break
    
    return locations

def main():
    try:
        # Get user input
        state = input("Enter state: ")
        city = input("Enter city: ")
        zip_code = input("Enter zip code: ")
        
        # Get coordinates from the address
        lat, lng = get_coordinates(state, city, zip_code)
        print(f"Coordinates for {city}, {state} {zip_code}: {lat}, {lng}")
        
        # Get infrastructures in the specified ZIP code
        infrastructures = get_infrastructures_in_zip(lat, lng, zip_code)
        print("\nInfrastructures within the ZIP code:")
        if infrastructures:
            for i, infra in enumerate(infrastructures, start=1):
                print(f"{i}. {infra['name']}")
                print(f"   Address: {infra['address']}")
                print(f"   Coordinates: {infra['lat']}, {infra['lng']}\n")
        else:
            print("No infrastructures found within the specified ZIP code.")
    
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
