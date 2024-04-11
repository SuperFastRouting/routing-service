import random

from django.test import TestCase, Client
from routing.app import routing

# Create your tests here.
class RouteTestCase(TestCase):
    def setUp(self):
        self.osm = routing.get_osm_data(debug=False)
        self.nodes_edges_tuple = routing.generate_nodes_and_edges(self.osm)
        self.num_actors = 5
        self.num_destinations = 10

        random_nodes = random.sample(range(1, len(self.nodes_edges_tuple[0])), self.num_destinations + 1)
        nodes_df = self.nodes_edges_tuple[0]

        self.source = nodes_df.iloc[random_nodes[0]]
        self.destinations = []
        for i in range(1, len(random_nodes)):
            self.destinations.append(nodes_df.iloc[random_nodes[i]])


    def test_post_to_route(self):
        client = Client()
        destination_points = []

        for i in range(0, self.num_destinations):
            destination_points.append({
                "longitude": self.destinations[i]['lon'],
                "latitude": self.destinations[i]['lat']
            })

        test_json = {
            "source": {
                "home_long": self.source['lon'],
                "home_lat": self.source['lat'],
            },
            "destinations": destination_points,
            "numTrucks": self.num_actors,
        }

        response = client.post("/routing/", test_json, content_type='application/json')
        print(response)
