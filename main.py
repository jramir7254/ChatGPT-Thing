#from locationsearch import generate_random_places
from flask import Flask, render_template, request
from graph import generate_folium_map
from chatgpt import get_random_places, get_response
from dotenv import load_dotenv
from openai import OpenAI
from lst import generate_random_places

import json


load_dotenv()

client = OpenAI()


app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])

def index():
    if request.method == 'POST':
        user_city = request.form['city']
        user_zip = request.form['zip']
        user_criterion = request.form['criterion']
        print(f'user city: {user_city}\nuser zip: {user_zip}')

        # Setting to True uses the Google Maps API, setting to False uses the ChatGPT API
        if True:
            locations = generate_random_places(user_zip)
            file_name = 'locations/generated_locations_google.json'
        else:
            locations = get_random_places(user_city, user_zip)
            file_name = 'locations/generated_locations_chatgpt.json'


        with open(file_name, "w") as file:
            json.dump(locations, file, indent=4)

        map_html = generate_folium_map(locations, user_zip)

        response = get_response("", "", user_criterion, locations, user_city)
        print(f'\n\n{response}\n\n')

        return render_template('index.html', locations=locations, map_html=map_html, response=response)
    else:
        return render_template("index.html")

app.run(host='0.0.0.0', port='81')