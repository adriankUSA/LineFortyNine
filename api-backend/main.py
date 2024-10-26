from math import radians, sin, cos, sqrt, atan2, pi
from flask import Flask, jsonify
import passiogo

app = Flask(__name__)

# Step 1: Identify the transportation system ID for UNC Charlotte
system_id = 1053
system = passiogo.getSystemFromID(system_id)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the PassioGo API Backend!"

# Step 2: Route to get all stops for the system
@app.route('/api/stops', methods=['GET'])
def get_live_bus_stops():
    try:
        stops = system.getStops()
        if not stops:
            return jsonify({"error": "No stops found"}), 404

        stops_data = [
            {
                "id": stop.id,
                "name": stop.name,
                "latitude": stop.latitude,
                "longitude": stop.longitude,
                "radius": stop.radius,
            }
            for stop in stops
        ]
        return jsonify(stops_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Step 3: Route to get real-time bus locations
@app.route('/api/vehicles', methods=['GET'])
def get_live_vehicle_data():
    try:
        vehicles = system.getVehicles()
        print("Available vehicles:", [vehicle.id for vehicle in vehicles])  # Debug: Print vehicle IDs

        if not vehicles:
            return jsonify({"error": "No vehicles found"}), 404

        vehicles_data = [
            {
                "id": vehicle.id,
                "name": vehicle.name,
                "type": vehicle.type,
                "route_id": vehicle.routeId,
                "route_name": vehicle.routeName,
                "longitude": vehicle.longitude,
                "latitude": vehicle.latitude,
                "speed": vehicle.speed,
                "pax_load": vehicle.paxLoad,
                "in_service": not vehicle.outOfService,
                "created": vehicle.created,
            }
            for vehicle in vehicles
        ]
        return jsonify(vehicles_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Haversine formula to calculate the shortest distance between two points on a sphere
def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Compute differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Ensure we use the shortest path across the globe by normalizing the longitude difference
    if abs(dlon) > pi:
        dlon = 2 * pi - abs(dlon)

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371000  # Earth's radius in meters

    return r * c  # Distance in meters


@app.route('/api/next-stop/<vehicle_id>', methods=['GET'])
def get_next_stop(vehicle_id):
    try:
        vehicles = system.getVehicles()
        vehicle = next((v for v in vehicles if str(v.id).strip() == str(vehicle_id).strip()), None)

        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        routes = system.getRoutes()
        route = next((r for r in routes if str(r.myid) == str(vehicle.routeId)), None)

        if not route:
            return jsonify({"error": f"Route with ID '{vehicle.routeId}' not found for vehicle"}), 404

        stops = route.getStops()
        if not stops or len(stops) < 2:
            return jsonify({"error": "Not enough stops on the route"}), 404

        # Assume the first stop is the current stop
        current_stop = stops[0]
        next_stop = stops[1]

        # Validate and swap lat/lon if necessary
        vehicle_lon = float(vehicle.longitude)

        # If the longitude looks like a latitude, swap it
        if vehicle_lon > 180 or vehicle_lon < -180:
            raise ValueError(f"Invalid longitude detected: {vehicle_lon}")
        
        vehicle_lat = float(current_stop.latitude)

        # Debugging print to verify the coordinates
        print(f"Vehicle Longitude: {vehicle_lon}, Current Stop Latitude: {vehicle_lat}")
        print(f"Next Stop Coordinates: {next_stop.latitude}, {next_stop.longitude}")

        # Calculate the distance to the next stop
        distance_to_stop = haversine(
            vehicle_lat, vehicle_lon,
            float(next_stop.latitude), float(next_stop.longitude)
        )

        return jsonify({
            "vehicle_id": vehicle.id,
            "route_name": route.name,
            "next_stop": next_stop.name,
            "next_stop_latitude": next_stop.latitude,
            "next_stop_longitude": next_stop.longitude,
            "vehicle_longitude": vehicle.longitude,
            "approx_distance_to_next_stop_meters": distance_to_stop
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True)
