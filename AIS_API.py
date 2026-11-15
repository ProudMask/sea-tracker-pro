"""Local vessel proximity API using explicitly synthetic positions."""
import math
from flask import Flask, jsonify, request

EARTH_RADIUS_KM = 6371.0088
DEMO_SHIPS = [
    {'ship_id': 1, 'name': 'Demo Pearl', 'latitude': 25.28, 'longitude': 55.29},
    {'ship_id': 2, 'name': 'Demo Horizon', 'latitude': 25.45, 'longitude': 55.43},
    {'ship_id': 3, 'name': 'Demo Voyager', 'latitude': 24.50, 'longitude': 54.40},
]


def coordinates(latitude, longitude):
    lat, lon = float(latitude), float(longitude)
    if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError('Latitude must be between -90 and 90 and longitude between -180 and 180; both must be finite.')
    return lat, lon


def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine great-circle distance in kilometers on a spherical Earth."""
    lat1, lon1 = coordinates(lat1, lon1)
    lat2, lon2 = coordinates(lat2, lon2)
    a1, a2 = math.radians(lat1), math.radians(lat2)
    delta_lat, delta_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    h = math.sin(delta_lat / 2) ** 2 + math.cos(a1) * math.cos(a2) * math.sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(min(1.0, max(0.0, h))))


def create_app(ships=None):
    app = Flask(__name__)
    catalog = [dict(ship) for ship in (DEMO_SHIPS if ships is None else ships)]
    for ship in catalog:
        coordinates(ship['latitude'], ship['longitude'])

    @app.get('/ships')
    def get_all_ships():
        return jsonify(catalog)

    @app.get('/ships/<int:ship_id>')
    def get_ship(ship_id):
        ship = next((s for s in catalog if s['ship_id'] == ship_id), None)
        return jsonify(ship) if ship is not None else (jsonify(error='Ship not found'), 404)

    @app.get('/nearby-ships')
    def get_nearby_ships():
        try:
            lat, lon = coordinates(request.args.get('latitude'), request.args.get('longitude'))
            radius = float(request.args.get('radius', 10))
            if not math.isfinite(radius) or radius < 0:
                raise ValueError('Radius must be finite and nonnegative, in kilometers.')
        except (TypeError, ValueError) as exc:
            return jsonify(error=f'Invalid query: {exc}'), 400
        results = []
        for ship in catalog:
            distance = calculate_distance(lat, lon, ship['latitude'], ship['longitude'])
            if distance <= radius:
                results.append({**ship, 'distance_km': distance})
        return jsonify(sorted(results, key=lambda s: (s['distance_km'], s['ship_id'])))

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
