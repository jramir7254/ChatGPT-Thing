from locationsearch import generate_random_places
from flask import Flask, render_template, request
from graph import generate_folium_map
from chatgpt import get_random_places
from dotenv import load_dotenv
from openai import OpenAI

import json


load_dotenv()

client = OpenAI()


app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])

def index():
    if request.method == 'POST':
        api_key = os.getenv("GOOGLE_API_KEY")
        user_city = request.form['city']
        user_zip = request.form['zip']
        print(f'user city: {user_city}\nuser zip: {user_zip}')

        # Setting to True uses the Google Maps API, setting to False uses the ChatGPT API
        if False:
            locations = generate_random_places(user_zip)
            file_name = 'locations/generated_locations_google.json'
        else:
            locations = get_random_places(user_city, user_zip)
            file_name = 'locations/generated_locations_chatgpt.json'


        with open(file_name, "w") as file:
            json.dump(locations, file, indent=4)

        map_html = generate_folium_map(locations)

        return render_template('index.html', locations=locations, map_html=map_html)
    else:
        return render_template("index.html")

app.run(host='0.0.0.0', port='80')