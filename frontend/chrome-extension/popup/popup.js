// DOM elements
const busStopSelect = document.getElementById("busStopName");
const busNameSelect = document.getElementById("busName");
const startButton = document.getElementById("startButton");

// Object to store bus data
const busData = {}; // { route_name: [stop_name1, stop_name2, ...] }

// Fetch all bus stops and populate the stops dropdown
async function fetchBusStops() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/stops');
        if (!response.ok) {
            throw new Error(`Failed to fetch stops: ${response.status}`);
        }
        const stops = await response.json();

        // Populate stops based on fetched data
        stops.forEach(stop => {
            const option = document.createElement("option");
            option.value = stop.name;
            option.textContent = stop.name;
            busStopSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching stops:', error);
    }
}

// Fetch all bus routes and store them in busData
async function fetchBusRoutes() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/vehicles');
        if (!response.ok) {
            throw new Error(`Failed to fetch vehicles: ${response.status}`);
        }
        const vehicles = await response.json();

        // Store route and bus data
        vehicles.forEach(vehicle => {
            if (!busData[vehicle.route_name]) {
                busData[vehicle.route_name] = [];
            }
            busData[vehicle.route_name].push(vehicle.name);
        });

        // Populate routes dropdown
        populateRoutes();
    } catch (error) {
        console.error('Error fetching vehicles:', error);
    }
}

// Populate routes dropdown based on fetched bus data
function populateRoutes() {
    Object.keys(busData).forEach(route => {
        const option = document.createElement("option");
        option.value = route;
        option.textContent = route;
        busNameSelect.appendChild(option);
    });
}

// Event listener to update the stop names when the route changes
busNameSelect.addEventListener("change", () => {
    const selectedRoute = busNameSelect.value;
    const stops = busData[selectedRoute] || [];

    // Clear existing stop options
    busStopSelect.innerHTML = "";

    // Populate new stop options based on selected route
    stops.forEach(stop => {
        const option = document.createElement("option");
        option.value = stop;
        option.textContent = stop;
        busStopSelect.appendChild(option);
    });
});

// Initialize the extension
document.addEventListener("DOMContentLoaded", async () => {
    await fetchBusStops();
    await fetchBusRoutes();
});
