"""Query the local demo API and optionally export notification drafts."""
import argparse
import json
import math
from pathlib import Path
import requests


def get_nearby_ships(base_url, latitude, longitude, radius):
    response = requests.get(f'{base_url.rstrip("/")}/nearby-ships', params={'latitude': latitude, 'longitude': longitude, 'radius': radius}, timeout=10)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError('API returned an unexpected response; expected a vessel list.')
    for ship in data:
        if not isinstance(ship, dict) or not {'ship_id', 'name', 'distance_km'} <= ship.keys():
            raise ValueError('API returned an invalid vessel record.')
        if not isinstance(ship['name'], str) or isinstance(ship['distance_km'], bool) or not isinstance(ship['distance_km'], (int, float)) or not math.isfinite(ship['distance_km']) or ship['distance_km'] < 0:
            raise ValueError('API returned an invalid vessel name or distance.')
    return data


def craft_email(ship):
    return (f'DRAFT — vessel proximity notification\n\n'
            f'{ship["name"]} is approximately {ship["distance_km"]:.2f} km from the selected reference point.\n'
            'Verify the position and service requirements before contacting the vessel operator.\n'
            'Demo positions are synthetic; this draft is not sent.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-url', default='http://127.0.0.1:5000')
    parser.add_argument('--latitude', type=float, default=25.28)
    parser.add_argument('--longitude', type=float, default=55.29)
    parser.add_argument('--radius', type=float, default=30, help='Radius in kilometers')
    parser.add_argument('--output', type=Path, help='Optional JSON output; existing file is replaced')
    args = parser.parse_args()
    try:
        ships = get_nearby_ships(args.api_url, args.latitude, args.longitude, args.radius)
        report = {'data_mode': 'synthetic_demo', 'reference': {'latitude': args.latitude, 'longitude': args.longitude}, 'radius_km': args.radius, 'vessel_count': len(ships), 'ships': ships, 'notification_drafts': [craft_email(s) for s in ships]}
        serialized = json.dumps(report, indent=2, allow_nan=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized + '\n', encoding='utf-8')
        print(serialized)
    except (requests.RequestException, ValueError, OSError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
