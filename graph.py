import networkx as nx
import matplotlib.pyplot as plt
import json

# Create a graph
G = nx.Graph()

# Add nodes (latitude, longitude)
with open("generated_locations.json", 'r') as file:
    data = json.load(file)
locations = {
    "A": (37.7749, -122.4194),  # San Francisco
    "B": (34.0522, -118.2437),  # Los Angeles
    "C": (36.7783, -119.4179),  # California
}

for name in data:
    G.add_node(name.get("name"), pos=(name.get("x-coordinate"), name.get("y-coordinate")))

# Add edges (connections between nodes)
#edges = [("A", "B"), ("A", "C"), ("B", "C")]
#G.add_edges_from(edges)

# Plot graph
pos = nx.get_node_attributes(G, 'pos')
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10)
plt.show()