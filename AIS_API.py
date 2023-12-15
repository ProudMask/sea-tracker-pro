from flask import Flask, jsonify, request
from flask_cors import CORS  # for handling cross-origin resource sharing
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Placeholder data for demonstration purposes
ais_data = [
    {"ship_id": 1, "name": "Ship1", "latitude": 34.0522, "longitude": -118.2437},
    {"ship_id": 2, "name": "Ship2", "latitude": 40.7128, "longitude": -74.0060},
    # Add more ships as needed
]

@app.route('/ships', methods=['GET'])
def get_all_ships():
    return jsonify(ais_data)

@app.route('/ships/<int:ship_id>', methods=['GET'])
def get_ship(ship_id):
    ship = next((s for s in ais_data if s['ship_id'] == ship_id), None)
    if ship:
        return jsonify(ship)
    else:
        return jsonify({"error": "Ship not found"}), 404

@app.route('/nearby-ships', methods=['GET'])
def get_nearby_ships():
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        radius = float(request.args.get('radius', 10))  # Default radius is 10 units (e.g., kilometers)

        nearby_ships = [s for s in ais_data if calculate_distance(latitude, longitude, s['latitude'], s['longitude']) <= radius]
        return jsonify(nearby_ships)

    except ValueError:
        return jsonify({"error": "Invalid input. Latitude, longitude, and radius must be numeric"}), 400

def calculate_distance(lat1, lon1, lat2, lon2):
    # Placeholder function for calculating distance between two points (you might need a more accurate formula)
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5

if __name__ == '__main__':
    app.run(debug=True)
