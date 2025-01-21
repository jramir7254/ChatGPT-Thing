from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
