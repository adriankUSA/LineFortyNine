from math import radians, sin, cos, sqrt, atan2, pi
import passiogo
from flask import Flask, jsonify
import passiogo
from datetime import datetime
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Step 1: Identify the transportation system ID for UNC Charlotte
system_id = 1053
system = passiogo.getSystemFromID(system_id)


@app.route('/', methods=['GET'])
def home():
    return "Welcome to the PassioGo API Backend!"

#Step 1.5: Retrieves all the oragnizations that use passiogo.
@app.route('/systems', methods = ['GET'])
def get_systems():
    system_dict = {}
    systems = passiogo.getSystems()
    if not systems:
        return jsonify({"error": "No systems were found"}), 404
    """for system in systems:
        system_dict[system.name] = system.id"""
    systems_data = [
        {
            'name': system.name,
            'id': system.id,
            'email': system.email,
            
        }
        for system in systems
    ]
    return jsonify(systems_data)

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


# Track previous state, last stop visited, and speed history
previous_vehicle_state = {}  # {vehicle_id: (lat, lon, timestamp, speed_history)}
last_visited_stop = {}  # {vehicle_id: last_stop_id}

# Track the state of each vehicle's route and stops
vehicle_route_memory = {}  # {vehicle_id: [(stop_id, arrival_time)]}

@app.route('/api/next-stop/<vehicle_id>', methods=['GET'])
def get_next_stop(vehicle_id):
    try:
        vehicles = system.getVehicles()
        vehicle = next((v for v in vehicles if str(v.id).strip() == str(vehicle_id).strip()), None)

        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        vehicle_lat = float(vehicle.latitude)
        vehicle_lon = float(vehicle.longitude)
        current_time = datetime.now()

        # Retrieve the route and stops
        routes = system.getRoutes()
        route = next((r for r in routes if str(r.myid) == str(vehicle.routeId)), None)

        if not route:
            return jsonify({"error": f"Route with ID '{vehicle.routeId}' not found for vehicle"}), 404

        stops = route.getStops()
        if not stops or len(stops) < 2:
            return jsonify({"error": "Not enough stops on the route"}), 404

        # Find the closest stop and the next stop dynamically
        closest_stop = min(stops, key=lambda stop: haversine(vehicle_lat, vehicle_lon, stop.latitude, stop.longitude))
        closest_index = stops.index(closest_stop)
        next_stop = stops[closest_index + 1] if closest_index + 1 < len(stops) else None

        if not next_stop:
            return jsonify({"error": "No more stops on the route"}), 404

        # Track the vehicle's progress through the route
        if vehicle_id not in vehicle_route_memory:
            vehicle_route_memory[vehicle_id] = []

        # Add the current stop to the memory if it's new
        if not vehicle_route_memory[vehicle_id] or vehicle_route_memory[vehicle_id][-1][0] != closest_stop.id:
            vehicle_route_memory[vehicle_id].append((closest_stop.id, current_time))

        # Calculate the average time between stops on the current route
        total_time = 0
        total_segments = 0

        # Iterate over the stored stops to calculate average time per segment
        for i in range(1, len(vehicle_route_memory[vehicle_id])):
            _, previous_time = vehicle_route_memory[vehicle_id][i - 1]
            _, current_stop_time = vehicle_route_memory[vehicle_id][i]

            segment_time = (current_stop_time - previous_time).total_seconds()
            total_time += segment_time
            total_segments += 1

        # Calculate the average time per segment (in seconds)
        avg_time_per_segment = total_time / total_segments if total_segments > 0 else 300  # Default 5 minutes

        # Calculate the distance to the next stop
        distance_to_next_stop = haversine(
            vehicle_lat, vehicle_lon, next_stop.latitude, next_stop.longitude
        )

        # Estimate speed (use distance and avg time per segment)
        if avg_time_per_segment > 0:
            estimated_speed = distance_to_next_stop / avg_time_per_segment  # Speed in m/s
        else:
            estimated_speed = 2.78  # Default to 10 km/h

        # Calculate estimated time to the next stop (seconds to minutes)
        time_to_next_stop_minutes = round(avg_time_per_segment / 60, 2)

        # Reset memory if the loop completes (e.g., first stop is reached again)
        if len(vehicle_route_memory[vehicle_id]) >= len(stops):
            vehicle_route_memory[vehicle_id] = []

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
            "estimated_speed_mps": estimated_speed
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
