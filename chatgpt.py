from locationsearch import search_all_place_types, get_zip_bounds
from dotenv import load_dotenv
from openai import OpenAI

import googlemaps
import requests
import folium
import random
import json
import os



load_dotenv()

client = OpenAI()


def get_response(city, zip):
    prompt = f'''
    Provide a list of up to 10 prominent locations, historical or representative of the area, that are typically 
    found within the ZIP code {zip} of the city of {city}.These locations do not need to be current, but they 
    should be commonly recognized places in that ZIP code area. Return the results in a JSON array, structured 
    as follows: ["name": "name", "address": "address"]. Do not include any additional text, explanations, or 
    formatting outside of the JSON.

    Ensure that all locations are strictly within the given ZIP code.
    '''
    
    return client.chat.completions.create(
        model="gpt-4o",  
        messages=[
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


def get_coords(address):
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        print(f"Address: {address}")
        print(f"Latitude: {lat}, Longitude: {lng}")
        return [lat, lng]
    else:
        print("Geocoding failed. No results found.")


def get_valid_addresses(parsed_json, user_zip):
    valid_addresses = []
    for place in parsed_json:
        zip_code = get_zip_code(place['address'])
        if zip_code == user_zip:
            print(f"Address '{place['name']}' is valid with ZIP code: {zip_code}")
            coordinates = get_coords(place['address'])
            coords = {"lat": coordinates[0], "lng": coordinates[1]}
            place['location'] = coords
            valid_addresses.append(place)
    return valid_addresses


def get_random_places(user_city, user_zip):
    response = get_response(user_city, user_zip).strip("```").strip("json")
    print(response)
    locations = get_valid_addresses(json.loads(response), user_zip)
    return locations