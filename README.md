# SeaTracker Pro

A reproducible maritime proximity prototype: query a local Flask API for synthetic vessels within a radius, rank them by distance, and export a JSON report with notification drafts. No paid API or credentials are needed. No emails are sent.

## Run the demo

Requires Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python AIS_API.py
```

In a second terminal, activate the same environment and run:

```bash
python main.py --latitude 25.28 --longitude 55.29 --radius 30 --output outputs/demo.json
```

The default example returns two synthetic vessels. Output includes full-precision `distance_km` values and draft notifications. Existing output files are replaced. This is a static demonstration, not live AIS tracking.

## API contract

| Endpoint | Behavior |
| --- | --- |
| `GET /ships` | List synthetic vessels |
| `GET /ships/1` | Retrieve a vessel, or return 404 |
| `GET /nearby-ships?latitude=25.28&longitude=55.29&radius=30` | Return vessels within 30 km, nearest first |

Latitude and longitude are required for proximity queries. Radius defaults to 10 km at the API. Coordinates must be finite and within geographic bounds; radius must be finite and nonnegative. Invalid queries return JSON with HTTP 400; valid queries with no nearby vessels return an empty list. The CLI explicitly defaults to a 30 km radius and calls this local API with a 10-second timeout.

## Method and limitations

Distance uses the Haversine formula with mean Earth radius 6371.0088 km. It measures approximate spherical great-circle distance, not sailing distance, travel time, navigability, or port entry. Filtering uses unrounded distance and includes the radius boundary. Data is static and synthetic; positions are not verified as navigable locations. No prediction model or real-world performance claim is included.

The former external API client and SMTP sending path are replaced by a consistent local demo and draft-only notifications. `--api-url` can point to a compatible trusted API, but output remains labeled as a synthetic demo; production ingestion requires an explicit data-provenance design.

## Verification

```bash
python -m unittest discover -s tests -v
```

Tests cover a known equatorial distance, the antimeridian, identical positions, radius filtering, invalid query values, empty results, missing vessels, client timeouts, and malformed responses.

## Portfolio extension

Add timestamped, licensed vessel observations and data quality checks. Then evaluate a defined question such as port-arrival time prediction using chronological splits, a simple baseline, MAE, and interval coverage. Keep this proximity prototype distinct from any future forecasting claims.
