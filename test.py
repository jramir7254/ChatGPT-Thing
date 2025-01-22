from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os

load_dotenv()

client = OpenAI()

google_api_key = os.getenv("GOOGLE_API_KEY")

def get_response():
    prompt = '''
    output the directions for the safest route from sams club 7001 Gateway Blvd W, El Paso, TX 79925 to Albertsons floral 2200 N Yarbrough Dr, El Paso, TX 79925
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


if __name__ == "__main__":
   # Basic route data
    routes = {
        "Route 1": [("Intersection A", 30), ("Intersection B", 45)],  # Time at each intersection
        "Route 2": [("Intersection X", 40), ("Intersection Y", 50)],
    }

    # Simulate normal traffic light timings
    normal_timings = {"green": 30, "red": 60}

    # Function to simulate adversarial manipulations
    def simulate_route(route, green_penalty=0, red_penalty=20):
        total_time = 0
        for intersection, normal_time in route:
            total_time += normal_time + green_penalty + red_penalty  # Adversarial delays
        return total_time

    # Compare routes
    for name, route in routes.items():
        manipulated_time = simulate_route(route, green_penalty=10, red_penalty=30)
        print(f"{name} takes {manipulated_time} seconds under manipulation.")

