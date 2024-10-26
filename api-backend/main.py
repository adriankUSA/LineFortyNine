from math import radians, sin, cos, sqrt, atan2, pi
import passiogo
from flask import Flask, jsonify
import passiogo
from datetime import datetime
import time

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


previous_vehicle_state = {}

@app.route('/api/next-stop/<vehicle_id>', methods=['GET'])
def get_next_stop(vehicle_id):
    try:
        # Retrieve all vehicles and find the matching one
        vehicles = system.getVehicles()
        vehicle = next((v for v in vehicles if str(v.id).strip() == str(vehicle_id).strip()), None)

        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        vehicle_lat = float(vehicle.latitude)
        vehicle_lon = float(vehicle.longitude)
        current_time = datetime.now()

        # Check if we have previous state for this vehicle
        if vehicle_id in previous_vehicle_state:
            prev_lat, prev_lon, prev_time = previous_vehicle_state[vehicle_id]
            # Calculate distance and time difference
            distance_traveled = haversine(vehicle_lat, vehicle_lon, prev_lat, prev_lon)
            time_diff = (current_time - prev_time).total_seconds()
            # Avoid division by zero
            speed_mps = distance_traveled / time_diff if time_diff > 0 else 0
        else:
            # Default speed if no previous data
            speed_mps = 0

        # Store the new state
        previous_vehicle_state[vehicle_id] = (vehicle_lat, vehicle_lon, current_time)

        # Find the matching route
        routes = system.getRoutes()
        route = next((r for r in routes if str(r.myid) == str(vehicle.routeId)), None)

        if not route:
            return jsonify({"error": f"Route with ID '{vehicle.routeId}' not found for vehicle"}), 404

        # Get all stops for the route
        stops = route.getStops()
        if not stops or len(stops) < 2:
            return jsonify({"error": "Not enough stops on the route"}), 404

        # Find the closest stop and the next stop
        closest_stop = min(stops, key=lambda stop: haversine(vehicle_lat, vehicle_lon, stop.latitude, stop.longitude))
        closest_index = stops.index(closest_stop)
        next_stop = stops[closest_index + 1] if closest_index + 1 < len(stops) else None

        if not next_stop:
            return jsonify({"error": "No more stops on the route"}), 404

        # Calculate the distance to the next stop
        distance_to_next_stop = haversine(
            vehicle_lat, vehicle_lon, next_stop.latitude, next_stop.longitude
        )

        # Calculate estimated time to the next stop
        if speed_mps > 0:
            time_to_next_stop_seconds = distance_to_next_stop / speed_mps
        else:
            time_to_next_stop_seconds = float('inf')  # Infinite time if bus is stationary

        # Convert time to minutes for better readability
        time_to_next_stop_minutes = time_to_next_stop_seconds / 60

        # Return the data as a JSON response
        return jsonify({
            "vehicle_id": vehicle.id,
            "route_name": route.name,
            "closest_stop": closest_stop.name,
            "next_stop": next_stop.name,
            "next_stop_latitude": next_stop.latitude,
            "next_stop_longitude": next_stop.longitude,
            "vehicle_latitude": vehicle_lat,
            "vehicle_longitude": vehicle_lon,
            "approx_distance_to_next_stop_meters": distance_to_next_stop,
            "estimated_time_to_next_stop_minutes": time_to_next_stop_minutes,
            "current_speed_mps": speed_mps
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
