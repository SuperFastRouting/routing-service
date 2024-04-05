import json

import osmnx as ox
import networkx as nx

from django.shortcuts import render
from django.http import JsonResponse

from shapely.geometry import Point

from routing.app import routing, clustering
from .models import Route

def route(request):
    """Routing Endpoint

    Parameters:
    request: Incoming HTTP Request

    Accepted Methods:
    GET: TBD
    POST: Generates a new route

    Returns:
    JsonResponse
    """

    if request.method == 'POST':
        request_body = json.loads(request.body)

        print(request_body)
        num_agents = request_body.get('numberOfActors')
        source_node_split = request_body.get('source').split(",")
        source_point = (float(source_node_split[0].strip()), float(source_node_split[1].strip()))

        destination_points = []
        for dest_point in request_body.get('destinations'):
            dest_node_split = dest_point.split(",")
            destination_points.append((float(dest_node_split[0].strip()), float(dest_node_split[1].strip())))

        # 60.538124, 26.931938 source
        # 60.523491, 26.945637 destination
        route_obj = Route.objects.create()

        print(route_obj.get_route_id())

        # For points, x = lon, y = lat
        # source_point = (26.931938, 60.538124)
        # destination_points = [
        #     (26.945637, 60.523491),
        #     (26.944521, 60.525898),
        #     (26.946527, 60.526283),
        # ]

        path_distance_tuple = generate_path_coordinates(
            request,
            source_point,
            destination_points,
            num_agents,
        )
        path_coordinates = path_distance_tuple[0]
        path_distances = path_distance_tuple[1]
        
        json_return = {
            "routeID": route_obj.get_numerical_id(),
            "paths": path_coordinates,
            "distances": path_distances,
        }

        print(json_return)

        return JsonResponse(json_return, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def generate_path_coordinates(request, source, targets, num_agents):
    """Generates coordinates for a generated shortest path

    Parameters:
    request: Incoming HTTP Request
    source: Source node
    targets: Target nodes
    num_agents (int): Number of agents from source

    Returns:
    (route_coords, distances) (tuple): Coordinates of every node on a route + total distance of route
    """
    # Generate OSM data reader
    osm = routing.get_osm_data(debug=True)

    # Generate nodes and edges of map
    nodes_edges_tuple = routing.generate_nodes_and_edges(osm)
    nodes_df = nodes_edges_tuple[0]
    edges_df = nodes_edges_tuple[1]

    # print("HERE")
    # print(nodes_edges_tuple)
    # print("HERE 2")
    # print(nodes_df.to_string())
    # print(edges_df.to_string())
    # print(nodes_df[nodes_df['id'] == 3684592331])

    # Generate working graph
    G = osm.to_graph(nodes_df, edges_df, graph_type="networkx")
    # print(source.x)
    # print(source.y)

    # Find nodes closest to given points
    source_node_id = ox.nearest_nodes(G, X=source[0], Y=source[1])
    source_node = nodes_df[nodes_df['id'] == source_node_id]
    source_coords = (source_node.iloc[0]['lon'], source_node.iloc[0]['lat'])

    target_nodes = []
    target_coords = []
    for target in targets:
        target_node_id = ox.nearest_nodes(G, X=target[0], Y=target[1])
        target_node = nodes_df[nodes_df['id'] == target_node_id]
        target_nodes.append(target_node_id)
        target_coords.append((target_node.iloc[0]['lon'], target_node.iloc[0]['lat']))
    print(source_coords)
    print(target_coords)

    # Cluster targets
    cluster_indices = clustering.hierarchal_cluster_nodes(target_coords, num_agents)
    destination_clusters = []
    for indices in cluster_indices:
        cluster = []
        for index in indices:
            cluster.append(target_nodes[index])
        destination_clusters.append(cluster)

    print("clusters: " + str(destination_clusters))

    # Generate routes
    routes = []
    distances = []
    for destinations in destination_clusters:
        route_distance_tuple = generate_single_path(G, source_node_id, destinations)
        route = route_distance_tuple[0]
        distance = route_distance_tuple[1]
        routes.append(route)
        distances.append(distance)


    print(routes)
    route_coords = []
    route_counter = 0
    
    for route_nodes in routes:
        route_coords.append([])
        
        for node_id in route_nodes:
            # try:
            node = nodes_df[nodes_df['id'] == node_id]
            node_coords = {
                "lon": node.iloc[0]['lon'],
                "lat": node.iloc[0]['lat'],
            }
            route_coords[route_counter].append(node_coords)
            # except Exception:
            #     print("No matching node found...")

        route_counter += 1

    return (route_coords, distances)

def generate_single_path(graph, origin, destinations):
    paths = [origin]
    path_length = 0

    if (len(destinations) != 1):
        nodes = find_destination_order(graph, origin, destinations, [])
        origin_node = origin
        for node in nodes:
            paths = paths + nx.shortest_path(graph, origin_node, node, method='dijkstra')[1:]
            path_length += nx.shortest_path_length(graph, origin_node, node, method='dijkstra')
            print("DISTANCE: ")
            print(path_length)
            origin_node = node
    else:
        paths = nx.shortest_path(graph, origin, destinations[0], method='dijkstra')
        path_length = nx.shortest_path_length(graph, origin, destinations[0], method='dijkstra')

    return (paths, path_length)

def find_destination_order(graph, source_node, dest_nodes, nodes_in_order):
    origin_node = source_node
    ordered_nodes = nodes_in_order
    destination_nodes = dest_nodes

    # Exit condition
    if (len(destination_nodes) == 1):
        nodes_in_order.append(destination_nodes[0])
        return nodes_in_order
    
    path_lengths = []
    for dest_node in destination_nodes:
        path_lengths.append(nx.shortest_path_length(graph, origin_node, dest_node))

    min_index = path_lengths.index(min(path_lengths))
    min_node = destination_nodes.pop(min_index)
    ordered_nodes.append(min_node)

    return find_destination_order(
        graph=graph,
        source_node=min_node,
        dest_nodes=destination_nodes,
        nodes_in_order=ordered_nodes,
    )
    


    
