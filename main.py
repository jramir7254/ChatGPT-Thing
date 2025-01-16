from flask import Flask, render_template, request
from dotenv import load_dotenv
from openai import OpenAI
import googlemaps
import requests
import json
import os


load_dotenv()
client = OpenAI()



def get_response(city, zip):
    prompt = f'''Provide a list of up to 20 prominent locations in the city of {city} that are strictly within 
                 or as close as possible to the ZIP code {zip}. Return the results in JSON format, structured as follows:
                 ["name": "name", "address": "address", "city": "city", "state": "state", "zip": "zip", "x-coordinate": x, "y-coordinate": y],
                 Do not include any additional text, explanations, or formatting outside of the JSON.
              '''
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

def print_coords(address):
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
    file = open("generated_locations.json", "w")
    for place in parsed_json:
        zip_code = get_zip_code(place.get("address"))
        if zip_code == user_zip:
            print(f"Address '{place.get("name")}' is valid with ZIP code: {zip_code}")
            res = print_coords(place.get("address"))
            lat = res[0]
            lng = res[1]
            place["x-coordinate"] = lat
            place["y-coordinate"] = lng
            json.dump(place, file, indent=4)
            valid_addresses.append(place)
    return valid_addresses




app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])

def index():
    if request.method == 'POST':
        user_city = request.form['city']
        user_zip = request.form['zip']
        response = get_response(user_city, user_zip).strip("```").strip("json")
        parsed_json = json.loads(response)

        # with open("generated_locations.json", "w") as file:
        #     json.dump(parsed_json, file, indent=4)

        valid_addresses = get_valid_addresses(parsed_json=parsed_json, user_zip=user_zip)
        return render_template('index.html', valid_addresses=valid_addresses)
    else:
        return render_template("index.html")

app.run(host='0.0.0.0', port='80')