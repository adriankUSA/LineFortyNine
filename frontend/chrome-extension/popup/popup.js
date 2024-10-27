// DOM elements
const busNameSelect = document.getElementById("busName");
const busInfoSelect = document.getElementById("busInfo");
const alertButton = document.getElementById("startAlertButton");

// Object to hold bus data
const busData = {};

// Fetch bus routes (names) from the API
async function fetchBusRoutes() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/vehicles');
        if (!response.ok) throw new Error('Failed to fetch vehicle data');
        
        const vehicles = await response.json();
        
        // Populate bus data structure
        vehicles.forEach(vehicle => {
            if (!busData[vehicle.route_name]) {
                busData[vehicle.route_name] = [];
            }
            busData[vehicle.route_name].push({ 
                name: vehicle.name, 
                id: vehicle.id 
            });
        });
        
        // Populate bus name dropdown
        populateBusNames();
        
    } catch (error) {
        console.error('Error fetching bus routes:', error);
    }
}

// Populate bus name options
function populateBusNames() {
    busNameSelect.innerHTML = ''; // Clear previous options
    Object.keys(busData).forEach(route => {
        const option = document.createElement("option");
        option.value = route;
        option.textContent = route;
        busNameSelect.appendChild(option);
    });
    
    // Trigger display for the first bus route in the list
    displayBusInfo();
}

// Fetch next stop and estimated time based on selected bus ID
async function fetchNextStopAndEstimatedTime(vehicleId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/next-stop/${vehicleId}`);
        if (!response.ok) throw new Error('Failed to fetch stop info');
        
        return await response.json(); // Expected response: { next_stop, estimated_time_to_next_stop_minutes }
        
    } catch (error) {
        console.error('Error fetching next stop and estimated time:', error);
        return null;
    }
}

// Display bus info based on the selected route
async function displayBusInfo() {
    const selectedRoute = busNameSelect.value;
    const buses = busData[selectedRoute] || [];
    
    busInfoSelect.innerHTML = ""; // Clear previous bus info
    
    for (const bus of buses) {
        const nextStopData = await fetchNextStopAndEstimatedTime(bus.id); // Fetch details
        const option = document.createElement("option");
        option.value = bus.id;
        
        if (nextStopData) {
            option.textContent = `Bus: ${bus.name}, Next Stop: ${nextStopData.next_stop}, ETA: ${nextStopData.estimated_time_to_next_stop_minutes} min`;
        } else {
            option.textContent = `Bus: ${bus.name}, Next Stop: N/A, ETA: N/A`;
        }
        
        busInfoSelect.appendChild(option);
    }
}

// Event listener for bus name selection
busNameSelect.addEventListener("change", displayBusInfo);

// Event listener for Start Alert button
alertButton.addEventListener("click", async () => {
    const selectedBusId = busInfoSelect.value;
    
    if (selectedBusId) {
        // Fetch latest details for the selected bus to set the alert
        const nextStopData = await fetchNextStopAndEstimatedTime(selectedBusId);
        
        if (nextStopData) {
            localStorage.setItem('selectedBusId', selectedBusId);
            alert(`Alert set for bus ETA updates! Next Stop: ${nextStopData.next_stop}, ETA: ${nextStopData.estimated_time_to_next_stop_minutes} min`);  // Confirm alert set
            console.log(`Alert set for bus with ID: ${selectedBusId}. Next Stop: ${nextStopData.next_stop}, ETA: ${nextStopData.estimated_time_to_next_stop_minutes} min`);
        } else {
            alert("Failed to fetch bus details for the alert.");
        }
    } else {
        alert("Please select a bus to set an alert.");
    }
});

// Function to continuously update bus information
async function updateBusInfo() {
    const selectedRoute = busNameSelect.value;
    const buses = busData[selectedRoute] || [];
    
    busInfoSelect.innerHTML = ""; // Clear previous bus info
    
    for (const bus of buses) {
        const nextStopData = await fetchNextStopAndEstimatedTime(bus.id); // Fetch latest details
        const option = document.createElement("option");
        option.value = bus.id;
        
        if (nextStopData) {
            option.textContent = `Bus: ${bus.name}, Next Stop: ${nextStopData.next_stop}, ETA: ${nextStopData.estimated_time_to_next_stop_minutes} min`;
        } else {
            option.textContent = `Bus: ${bus.name}, Next Stop: N/A, ETA: N/A`;
        }
        
        busInfoSelect.appendChild(option);
    }
}

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
    await fetchBusRoutes();
    
    // Set interval to update bus info every 30 seconds
    setInterval(updateBusInfo, 30000);
});

