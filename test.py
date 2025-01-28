import json
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
from geopy.distance import geodesic
import heapq
from scipy.spatial import Delaunay
import numpy as np
import numpy as np
from PyPDF2 import PdfReader
import requests
import os
import networkx as nx
import matplotlib.pyplot as plt
from math import sqrt



load_dotenv()

client = OpenAI()

google_api_key = os.getenv("GOOGLE_API_KEY")

def get_response(pdf):
    prompt = f'''
    Summarize the following in six sentences or less: {pdf}
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

def generate_pdf():
    # Load the PDF file
    from fpdf import FPDF

    # Create PDF instance
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add content
    pdf.cell(200, 10, txt="Hello, FPDF!", ln=True, align='C')
    pdf.multi_cell(0, 10, txt="This is a sample PDF created using Python's FPDF library.")

    # Save the PDF
    file_name = "example_fpdf.pdf"
    pdf.output(file_name)
    print(f"PDF created: {file_name}")

def calculate_distance(coord1, coord2):
    return sqrt((coord1['lat'] - coord2['lat'])**2 + (coord1['lng'] - coord2['lng'])**2)


if __name__ == "__main__":
    # Load coordinates

    with open("locations/generated_locations_google.json", 'r') as file:
        data = json.load(file)
    coordinates = {}
    for place in data:
        coordinates[place['name']] = (place['location']['lat'], place['location']['lng'])

    G = nx.DiGraph()  # Directed graph
    with open("locations_with_coords_weights.txt", 'r') as output_lines_with_coords:
        for line in output_lines_with_coords:
            # Parse the updated .txt data
            line = line.strip().strip("()")
            source, destination, weight, src_lat, src_lng, dest_lat, dest_lng = line.split(", ")
            G.add_edge(source, destination, weight=float(weight))

    # Extract coordinates for plotting
    node_positions = {node: (lng, lat) for node, (lat, lng) in coordinates.items()}

    # Plot the graph with the coordinates
    plt.figure(figsize=(10, 8))
    nx.draw(
        G,
        pos=node_positions,
        with_labels=True,
        node_color="lightblue",
        node_size=2000,
        font_size=10,
        edge_color="gray",
    )
    # Add edge weights as labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos=node_positions, edge_labels={(u, v): f"{d:.2f}" for u, v, d in G.edges(data="weight")})

    plt.title("Graph of Locations with Coordinates")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()