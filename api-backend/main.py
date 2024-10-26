import requests
from flask import Flask, jsonify

app = Flask(__name__)

PASSIOGO_API_URL = "https://api.passiogo.com"

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the PassioGo API!"


@app.route('/api/stops', methods=['GET'])
def get_live_bus_stops():
     # Replace 'path-to-endpoint' with the actual API path for stops

    try: 
        response = requests.get(f"{PASSIOGO_API_URL}/stops")
        response.raise_for_status()
        stops_data = response.json()
        return jsonify(stops_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)