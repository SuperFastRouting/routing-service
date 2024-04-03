import osmnx as ox
import networkx as nx

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from shapely.geometry import Point

from routing.app import routing
from .models import Route

def index(request):
    # 60.538124, 26.931938 source
    # 60.523491, 26.945637 destination
    route_obj = Route.objects.create()

    print(route_obj.get_route_id())

    source_point = Point(26.931938, 60.538124)
    destination_point = Point(26.945637, 60.523491)

    path_coordinates = generate_path_coordinates(request, source_point, destination_point)
    
    json_return = {
        "routeID": route_obj.get_numerical_id(),
        "paths": path_coordinates,
    }

    print(json_return)

    return JsonResponse(json_return, status=200)

def generate_path_coordinates(request, source, target):
    # For Points, x = lon, y = lat
    osm = routing.get_osm_data()

    nodes_edges_tuple = routing.generate_nodes_and_edges(osm)
    nodes_df = nodes_edges_tuple[0]
    edges_df = nodes_edges_tuple[1]

    print("HERE")
    print(nodes_edges_tuple)
    print("HERE 2")
    # print(nodes_df.to_string())
    # print(edges_df.to_string())
    print(nodes_df[nodes_df['id'] == 3684592331])

    G = osm.to_graph(nodes_df, edges_df, graph_type="networkx")

    print(source.x)
    print(source.y)
    source_node = ox.nearest_nodes(G, X=source.x, Y=source.y)
    target_node = ox.nearest_nodes(G, X=target.x, Y=target.y)

    print(source_node)
    print(target_node)

    route_nodes = nx.shortest_path(G, source_node, target_node, method='dijkstra')
    route_coords = []
    
    for node_id in route_nodes:
        try:
            node = nodes_df[nodes_df['id'] == node_id]
            node_coords = (node.iloc[0]['lon'], node.iloc[0]['lat'])
            print(type(node))
            route_coords.append(node_coords)
        except Exception:
            print("No matching node found...")


    return route_coords
