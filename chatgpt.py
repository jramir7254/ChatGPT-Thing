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
    Generates a structured assignment prompt based on Bloom’s Taxonomy,
    adversarial thinking, and graph-based routing.

    Also generates a `.txt` file with weighted edges representing the graph.
    """

    # Define the system-level instruction
    system_instruction = """
    Your task is to develop an assignment that encourages students or professors 
    to engage with graph principles, adversarial thinking, Bloom's Taxonomy, 
    and geographical familiarity using provided location data and criteria. 
    This tool is designed to empower users in creating educational graph-based 
    tasks that incorporate both analytical and creative thinking methodologies.

    ## Steps

    1. **Input Collection:**
      - User inputs a zip code and criteria (e.g., fastest or safest route).
      - Use Google Maps API to generate ten random locations within the specified zip code area.

    2. **Graph Generation:**
      - Convert the generated locations into a graph data structure in a `.txt` file 
        with fields: (source, destination, weight).
      - Ensure weights are based on the user's criteria.

    3. **Assignment Creation:**
      - Parse the `.txt` file containing the graph data.
      - Incorporate elements of adversarial thinking and select one Bloom’s Taxonomy 
        level to focus the assignment on (e.g., Creating, Analyzing).
      - Design an engaging assignment task related to graph theory principles 
        and adversarial scenarios.

    4. **Incorporate 'Sense of Belonging':**
      - Emphasize the familiarity of the locations based on the user’s zip code 
        to add a personal and local dimension to the assignment.

    ## Output Format

    The assignment should be structured as follows:
    - **Title:** A descriptive assignment name.
    - **Introduction:** Explain graph theory and adversarial thinking.
    - **Task:** Provide clear instructions, incorporating adversarial analysis.
    - **Student Expectations:** What students should analyze or build.
    - **Guidelines:** Ensure alignment with Bloom's Taxonomy.
    - **Critical Thinking Prompts:** Encourage analytical reasoning.

    ## Example Output:

    **Title:** Enhancing Safety in Your Neighborhood: Analyzing Local Routes

    **Introduction:**
    In graph theory, nodes and edges create a framework for understanding interconnected 
    processes. This assignment integrates graph principles with adversarial thinking 
    to foster a deeper understanding of route safety within familiar locales.

    **Task:**
    Using the graph data provided based on your entered zip code and the criterion 
    of safety, analyze and evaluate the interconnected paths. Identify vulnerabilities 
    and propose enhancements to safety.

    **Submission Guidelines:**
    Compile analysis into a structured report using Bloom’s Analyzing framework.
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
    Generate a structured assignment based on the following parameters:

    - **ZIP Code:** {zip_code}
    - **Criteria:** {criteria}
    - **Bloom’s Taxonomy Level:** {bloom_level}
    - **Locations:** {locations}

    Follow the system instruction to ensure correct formatting and emphasis on graph-based 
    adversarial thinking and educational goals.
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
    Converts the structured assignment text into a well-formatted PDF.
    Includes bold headings and structured sections for easy readability.
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set default font
    pdf.set_font("Arial", "", 12)

    # Add title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Graph-Based Adversarial Thinking Assignment", ln=True, align="C")
    pdf.ln(10)

    # Normalize Unicode characters that might cause encoding issues
    assignment_text = assignment_text.replace("’", "'").replace("“", '"').replace("”", '"').replace("—", "-")

    # Define section markers for structured formatting
    sections = {
        "Title": "B",
        "Introduction": "B",
        "Task": "B",
        "Student Expectations": "B",
        "Guidelines": "B",
        "Critical Thinking Prompts": "B",
        "Expected Output": "B",
        "Bloom’s Alignment": "B"
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
            # Regular text
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
    pdf.output(pdf_filename, "F")  # Force UTF-8 compatible encoding
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