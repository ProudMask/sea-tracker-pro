import unittest
from unittest.mock import Mock, patch
import requests
from AIS_API import create_app, calculate_distance
from main import get_nearby_ships, craft_email


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app([
            {'ship_id': 1, 'name': 'Origin', 'latitude': 0, 'longitude': 0},
            {'ship_id': 2, 'name': 'East', 'latitude': 0, 'longitude': 1},
        ]).test_client()

    def test_known_distances(self):
        self.assertEqual(calculate_distance(0, 0, 0, 0), 0)
        self.assertAlmostEqual(calculate_distance(0, 0, 0, 1), 111.195, places=3)
        self.assertAlmostEqual(calculate_distance(0, 179, 0, -179), 222.390, places=3)

    def test_filter_and_order(self):
        data = self.client.get('/nearby-ships?latitude=0&longitude=0&radius=112').get_json()
        self.assertEqual([s['ship_id'] for s in data], [1, 2])
        self.assertEqual(len(self.client.get('/nearby-ships?latitude=0&longitude=0&radius=111').get_json()), 1)
        self.assertEqual(len(self.client.get('/nearby-ships?latitude=0&longitude=0&radius=0').get_json()), 1)

    def test_invalid_queries(self):
        for query in ('', 'latitude=0', 'latitude=no&longitude=0', 'latitude=91&longitude=0', 'latitude=0&longitude=181', 'latitude=nan&longitude=0', 'latitude=0&longitude=0&radius=-1', 'latitude=0&longitude=0&radius=inf'):
            with self.subTest(query=query):
                self.assertEqual(self.client.get('/nearby-ships?' + query).status_code, 400)

    def test_missing_and_empty(self):
        self.assertEqual(self.client.get('/ships/999').status_code, 404)
        self.assertEqual(self.client.get('/nearby-ships?latitude=30&longitude=30&radius=1').get_json(), [])
        self.assertEqual(create_app([]).test_client().get('/ships').get_json(), [])

    @patch('main.requests.get')
    def test_client_contract(self, get):
        get.return_value = Mock()
        get.return_value.json.return_value = [{'ship_id': 1, 'name': 'Demo', 'distance_km': 2.5}]
        ships = get_nearby_ships('http://localhost:5000/', 0, 0, 10)
        self.assertEqual(ships[0]['distance_km'], 2.5)
        self.assertEqual(get.call_args.kwargs['timeout'], 10)
        self.assertIn('not sent', craft_email(ships[0]))

    @patch('main.requests.get')
    def test_invalid_response_and_timeout(self, get):
        for payload in ({'error': 'unexpected'}, [{}], [{'ship_id': 1, 'name': 'Demo', 'distance_km': float('nan')}]):
            get.return_value.json.return_value = payload
            with self.assertRaises(ValueError):
                get_nearby_ships('http://localhost:5000', 0, 0, 10)
        get.side_effect = requests.Timeout('timed out')
        with self.assertRaises(requests.Timeout):
            get_nearby_ships('http://localhost:5000', 0, 0, 10)


if __name__ == '__main__':
    unittest.main()
