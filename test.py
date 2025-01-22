from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os

load_dotenv()

client = OpenAI()

google_api_key = os.getenv("GOOGLE_API_KEY")

def get_response():
    prompt = '''output the directions for the safest route from sams club 7001 Gateway Blvd W, El Paso, TX 79925 to Albertsons floral 2200 N Yarbrough Dr, El Paso, TX 79925
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
    print(get_response())
