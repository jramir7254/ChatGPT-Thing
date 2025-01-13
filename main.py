from openai import OpenAI
from flask import Flask, render_template, request
import requests
import json

client = OpenAI()

def get_response(city, zip):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"""Give me a list of five coordinates, along with the name
                 the establishment/landmark and their zip code, of prominent locations in the city of 
                 {city} that are ONLY within the zip code {zip}."""
            }
        ]
    )#.choices[0].message.content
    print(completion.choices[0].message)
    return completion.choices[0].message.content


app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])

def index():
    if request.method == 'POST':
        user_city = request.form['city']
        user_zip = request.form['zip']
        response = get_response(user_city, user_zip)
        return render_template('index.html', response=response)
    else:
        return render_template("index.html")

app.run(host='0.0.0.0', port='80')