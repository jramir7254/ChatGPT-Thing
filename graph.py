import os
import googlemaps
import matplotlib.pyplot as plt
import networkx as nx
import folium
import json

# Load your Google Maps API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Ensure your .env file contains the key

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

def get_zipcode_boundaries(zip_code):
    """Fetches the boundary coordinates (polygon) for a given ZIP code"""
    result = gmaps.geocode(zip_code)

    if result and "geometry" in result[0]:
        bounds = result[0]["geometry"]["bounds"]
        northeast = bounds["northeast"]
        southwest = bounds["southwest"]

        # Return bounding box (not exact polygon, but useful for visualization)
        return [
            (northeast["lat"], northeast["lng"]),
            (southwest["lat"], northeast["lng"]),
            (southwest["lat"], southwest["lng"]),
            (northeast["lat"], southwest["lng"]),
            (northeast["lat"], northeast["lng"]),  # Close the polygon
        ]
    return None



# Generates and loads a map with all markers from data and stores into an HTML file
def generate_folium_map(locations, zip_code):
    folium_map = folium.Map(location=[37.7749, -122.4194], zoom_start=6)
    for location in locations:
        folium.Marker(location=(location["location"]["lat"], location["location"]["lng"]), popup=location["name"]).add_to(folium_map)
        
    boundary_coords = get_zipcode_boundaries(zip_code)
    
    if boundary_coords:
        # Add polygon representing ZIP code boundary
        folium.Polygon(
            locations=boundary_coords,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.2
        ).add_to(folium_map)
    folium_map.save('templates/map_graph.html')
    return folium_map._repr_html_()


# Generates a graph-node represenation of the locations inside data
def generate_graph():
    with open("generated_locations.json", 'r') as file:
        data = json.load(file)
    G = nx.Graph()
    for name in data:
        G.add_node(name.get("name"), pos=(name.get("x-coordinate"), name.get("y-coordinate")))
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10)
    plt.show()