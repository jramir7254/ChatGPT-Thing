import matplotlib.pyplot as plt
import networkx as nx
import folium
import json



# Generates and loads a map with all markers from data and stores into an HTML file
def generate_folium_map(locations):
    folium_map = folium.Map(location=[37.7749, -122.4194], zoom_start=6)
    for location in locations:
        folium.Marker(location=(location["location"]["lat"], location["location"]["lng"]), popup=location["name"]).add_to(folium_map)
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