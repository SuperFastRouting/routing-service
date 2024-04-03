import os
import pandas

import pyrosm
from pyrosm import get_data, OSM
import osmnx as ox
import networkx as nx

def plot_drivables(osm):
    # Generate chart for drivable roads
    drive_net = osm.get_network(network_type="driving")
    print(type(drive_net))
    print(drive_net)
    drive_net.plot()

def calculate_basic_route(osm):
    # nodes, edges = osm.get_network(nodes=True)
    nodes, edges = osm.get_network(network_type="driving", nodes=True)

    # ax = edges.plot(figsize=(6,6), color="gray")
    # ax = nodes.plot(ax=ax, color="red", markersize=2.5)
    print(edges.head())
    G = osm.to_graph(nodes, edges, graph_type="networkx")
    # ox.plot_graph(G)

    # Basic routing
    source_address = "Bulevardi 5, Helsinki"
    target_address = "Unioninkatu 40, Helsinki"

    source = ox.geocode(source_address)
    target = ox.geocode(target_address)

    print(source)
    print(target)

    source_node = ox.nearest_nodes(G, source[0], source[1])
    target_node = ox.nearest_nodes(G, target[0], target[1])

    print(source_node)
    print(target_node)

    route = nx.shortest_path(G, source_node, target_node, weight="length")
    print(route)
    # fig, ax = ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k')

def generate_nodes_and_edges(osm):
    nodes, edges = osm.get_network(network_type="driving", nodes=True)
    
    return (nodes, edges)

def get_osm_data():
    dir = os.getcwd()
    print(dir)
    fp = get_data("calgary", directory="routing/data")
    # osm = OSM(fp)
    osm = OSM(get_data("test_pbf"))

    return osm

def main():
    fp = get_data("calgary", directory="./data")
    print(fp)

    # Initialize OSM parser
    osm = OSM(fp)
    
    # osm = OSM(get_data("test_pbf"))
    print(type(osm))
    
    plot_drivables(osm=osm)

    calculate_basic_route(osm=osm)

    
    # End
    return 0

if __name__ == '__main__':
    main()