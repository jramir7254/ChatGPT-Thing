from fpdf import FPDF
from locationsearch import search_all_place_types, get_zip_bounds
from dotenv import load_dotenv
from openai import OpenAI

import googlemaps
import requests
import folium
import random
import json
import os


client = OpenAI()

def get_response(city, zip_code, criteria, locations, bloom_level):
    """
    Generates a structured **Java-based** assignment that incorporates adversarial 
    graph analysis, route manipulation, and security considerations.
    
    Also generates a `.txt` file with weighted edges representing the graph.
    """

    # System-wide instruction for GPT to generate Java-based coding assignments
    system_instruction = """
    Your task is to develop a **Java-based** assignment that engages students with:
    - Graph theory principles
    - Adversarial thinking (attacks on shortest paths, node removals)
    - Bloom's Taxonomy (learning-focused objectives)
    - Geographical familiarity (sense of belonging via ZIP code data)

    ## Assignment Format:
    - **Title:** A descriptive, engaging name.
    - **Introduction:** Explain graph theory, adversarial risks, and localized routing.
    - **Programming Task:** Implement graph-based adversarial analysis in **Java**.
    - **Code Requirements:**  
      - Must include **Graph representation in Java** (use `HashMap`, `ArrayList`, `Graph` class).
      - Implement **Dijkstra’s Algorithm** (or an alternative).
      - Simulate **malicious edge modifications** (increase weights to reroute traffic).
      - Implement **countermeasures** (validate shortest paths, detect irregularities).
    - **Expected Output:** Java-based program solving the problem.
    - **Adversarial Angle:** Focus on **attack detection** and **graph resilience**.
    - **Sense of Belonging:** Emphasize using **familiar, local locations**.

    ## Example Java Programming Tasks:
    1. **Detecting Route Manipulation:** Write a Java program that flags suspicious weight changes.
    2. **Graph Resilience Testing:** Simulate adversarial attacks that remove nodes from a Java-based graph.
    3. **Optimized Path Recovery:** Design an algorithm that recalculates shortest paths after manipulation.

    **Each task must include:**  
    - **Java code implementation details**  
    - **Graph-based problem-solving**  
    - **Security and adversarial considerations**  
    - **Real-world applications**  
    """

    # Generate weighted edges for the graph
    edges = []
    for i in range(len(locations) - 1):
        source = locations[i]["name"]
        destination = locations[i + 1]["name"]
        weight = random.randint(5, 50) if criteria == "Fastest Route" else random.randint(1, 10)
        edges.append(f"{source},{destination},{weight}")

    # Save graph data to a .txt file
    graph_filename = f"graph_{zip_code}.txt"
    with open(graph_filename, "w") as file:
        file.write("Source,Destination,Weight\n")
        file.write("\n".join(edges))

    # Generate the structured assignment
    user_prompt = f"""
    Generate a **Java-based graph analysis assignment** using the following parameters:

    - **ZIP Code:** {zip_code}
    - **Criteria:** {criteria}
    - **Bloom’s Taxonomy Level:** {bloom_level}
    - **Locations:** {locations}

    Ensure the output follows the structured format and includes:
    - **Graph manipulation in Java** (use `HashMap`, `ArrayList`)
    - **Adversarial attack simulation or detection**
    - **Real-world security implications**
    """

    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    ).choices[0].message.content

    generate_assignment_pdf(response)
    return response

def generate_assignment_pdf(assignment_text, graph_filename=None, pdf_filename="assignment.pdf"):
    """
    Converts a **Java-based** structured assignment into a **well-formatted PDF**, ensuring:
    - **Bold headings** for section clarity
    - **Monospace font** for Java code snippets
    - **Graph reference** if a `.txt` file is included
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set title font
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Java-Based Graph Security Assignment", ln=True, align="C")
    pdf.ln(10)

    # Normalize Unicode characters that might cause encoding issues
    assignment_text = assignment_text.replace("’", "'").replace("“", '"').replace("”", '"').replace("—", "-")

    # Define section markers for structured formatting
    sections = {
        "Title": "B",
        "Introduction": "B",
        "Programming Task": "B",
        "Code Requirements": "B",
        "Expected Output": "B",
        "Adversarial Angle": "B",
        "Sense of Belonging": "B"
    }

    pdf.set_font("Arial", "", 12)
    lines = assignment_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines

        # Detect and format section headings
        for section in sections:
            if line.startswith(section):
                pdf.set_font("Arial", sections[section], 14)
                pdf.cell(0, 8, line, ln=True)
                pdf.set_font("Arial", "", 12)  # Reset to regular font after heading
                pdf.ln(4)  # Add spacing after section title
                break
        else:
            # Detect and format Java code blocks
            if "```java" in line or "```" in line:
                pdf.set_font("Courier", "", 11)  # Monospace for Java code
            else:
                pdf.set_font("Arial", "", 12)  # Regular text
            pdf.multi_cell(0, 7, line.strip())
            pdf.ln(3)  # Line spacing

    # Add Graph File Reference (if available)
    if graph_filename:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Graph Data (.txt) File:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"The graph file generated for this assignment is: {graph_filename}", ln=True)

    # Save the PDF
    pdf.output(pdf_filename, "F")
    print(f"✅ PDF successfully saved as {pdf_filename}")



# def get_zip_code(address):
#     geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
#     params = {
#         "address": address,
#         "key": os.getenv("GOOGLE_API_KEY")
#     }
    
#     response = requests.get(geocoding_url, params=params)
#     if response.status_code == 200:
#         data = response.json()
#         if "results" in data and len(data["results"]) > 0:
#             for component in data["results"][0]["address_components"]:
#                 if "postal_code" in component["types"]:
#                     return component["long_name"]  # Return the ZIP code
#     return None  # Return None if ZIP code is not found


# def get_coords(address):
#     gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))
#     geocode_result = gmaps.geocode(address)
#     if geocode_result:
#         location = geocode_result[0]['geometry']['location']
#         lat, lng = location['lat'], location['lng']
#         print(f"Address: {address}")
#         print(f"Latitude: {lat}, Longitude: {lng}")
#         return [lat, lng]
#     else:
#         print("Geocoding failed. No results found.")


# def get_valid_addresses(parsed_json, user_zip):
#     valid_addresses = []
#     for place in parsed_json:
#         zip_code = get_zip_code(place['address'])
#         if zip_code == user_zip:
#             print(f"Address '{place['name']}' is valid with ZIP code: {zip_code}")
#             coordinates = get_coords(place['address'])
#             coords = {"lat": coordinates[0], "lng": coordinates[1]}
#             place['location'] = coords
#             valid_addresses.append(place)
#     return valid_addresses


def get_random_places(user_city, user_zip):
    response = get_response(user_city, user_zip).strip("```").strip("json")
    print(response)
    locations = get_valid_addresses(json.loads(response), user_zip)
    return locations