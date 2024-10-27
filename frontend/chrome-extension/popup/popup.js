// DOM elements
const busNameSelect = document.getElementById("busName");
const busInfoSelect = document.getElementById("busInfo");

// Object to hold bus data
const busData = {}; // { route_name: [{ name: bus_name, id: bus_id }, ...] }

// Fetch bus routes (names) from the API
async function fetchBusRoutes() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/vehicles');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const vehicles = await response.json();
        vehicles.forEach(vehicle => {
            if (!busData[vehicle.route_name]) {
                busData[vehicle.route_name] = [];
            }
            // Store bus name and ID
            busData[vehicle.route_name].push({ 
                name: vehicle.name, 
                id: vehicle.id 
            });
        });
        populateBusNames();
    } catch (error) {
        console.error('Error fetching bus routes:', error);
    }
}

// Populate bus name options
function populateBusNames() {
    Object.keys(busData).forEach(route => {
        const option = document.createElement("option");
        option.value = route;
        option.textContent = route;
        busNameSelect.appendChild(option);
    });
}

// Fetch next stop and estimated time based on selected bus ID
async function fetchNextStopAndEstimatedTime(vehicleId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/next-stop/${vehicleId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json(); // Assuming the response is in JSON format
    } catch (error) {
        console.error('Error fetching next stop and estimated time:', error);
        return null;
    }
}

// Display buses and their next stops and estimated times based on selected bus name
async function displayBusInfo() {
    const selectedRoute = busNameSelect.value;
    const buses = busData[selectedRoute] || [];

    // Clear previous bus info
    busInfoSelect.innerHTML = ""; // Clear previous options

    // Populate bus information dropdown
    for (const bus of buses) {
        const nextStopData = await fetchNextStopAndEstimatedTime(bus.id); // Fetch next stop details
        const option = document.createElement("option");
        option.value = bus.id; // Use bus ID as the value
        
        // Display bus name, next stop, and estimated time
        if (nextStopData) {
            option.textContent = `Bus: ${bus.name}, Next Stop: ${nextStopData.next_stop}, ETA: ${nextStopData.estimated_time_to_next_stop_minutes} min`;
        } else {
            option.textContent = `Bus: ${bus.name}, Next Stop: N/A, Estimated Time: N/A`;
        }

        busInfoSelect.appendChild(option);
    }
}

// Event listener for bus name selection
busNameSelect.addEventListener("change", displayBusInfo);

// Initialize the extension
document.addEventListener("DOMContentLoaded", async () => {
    await fetchBusRoutes();
    displayBusInfo(); // Display bus info for the default selection
});
