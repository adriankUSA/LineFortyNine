import passiogo
from flask import Flask, jsonify

app = Flask(__name__)

# Step 1: Identify the transportation system ID (Replace with correct ID for UNC Charlotte)
system_id = 1068  # Example ID, update if needed
system = passiogo.getSystemFromID(system_id)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the PassioGo API Backend!"

# Step 2: Define the route to get all stops for this system
@app.route('/api/stops', methods=['GET'])
def get_live_bus_stops():
    try:
        # Retrieve all stops for the system
        stops = system.getStops()
        
        # Convert each stop to a dictionary for JSON serialization
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

        # Return the serialized stop data as JSON
        return jsonify(stops_data), 200

    except Exception as e:
        # Return the error message if something goes wrong
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
