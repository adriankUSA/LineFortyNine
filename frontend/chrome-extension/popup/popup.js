//elements
const busStopNameElement = document.getElementById("busStopName")
const busNameElement = document.getElementById("busName")

//Button elements
const startButton = document.getElementById("startButton")
const stopButton= document.getElementById("endButton")

startButton.onclick = function() {
  console.log("Clicked start");
}

busStopNameElement.onchange = function() {
  const selectedValue = busStopNameElement.value;
  console.log("Dropdown changed to:", selectedValue);
};

busNameElement.onchange = function() {
  const selectedValue = busNameElement.value;
  console.log("Dropdown changed to:", selectedValue);
};

async function fetchBusRoutes() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/vehicles');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const vehicles = await response.json();
    console.log('Fetched vehicles:', vehicles); // Log the fetched data
    vehicles.forEach(vehicle => {
      busData[vehicle.route_name] = []; // Initialize an empty array for each route
    });
    populateBusStops();
  } catch (error) {
    console.error('Error fetching bus routes:', error);
  }
}

async function fetchBusStops() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/stops');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const stops = await response.json();
    console.log('Fetched stops:', stops); // Log the fetched data
    stops.forEach(stop => {
      // Assume each stop has a 'name' and 'route_name' property
      if (busData[stop.route_name]) {
        busData[stop.route_name].push(stop.name);
      }
    });
  } catch (error) {
    console.error('Error fetching bus stops:', error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const busStopSelect = document.getElementById("busStopName");
  const busNameSelect = document.getElementById("busName");

  // Object to hold bus data
  const busData = {};

  // Fetch bus stops from the API and populate the dropdown
  async function fetchBusStops() {
      try {
          const response = await fetch('http://127.0.0.1:5000/api/stops');
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          const stops = await response.json();
          stops.forEach(stop => {
              const option = document.createElement("option");
              option.value = stop.name;
              option.textContent = stop.name;
              busStopSelect.appendChild(option);
          });
      } catch (error) {
          console.error('Error fetching bus stops:', error);
      }
  }

  // Fetch vehicle routes from the API
  async function fetchBusRoutes() {
      try {
          const response = await fetch('http://127.0.0.1:5000/api/vehicles');
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          const vehicles = await response.json();
          vehicles.forEach(vehicle => {
              busData[vehicle.route_name] = vehicle.name;
          });
          populateRoutes();
      } catch (error) {
          console.error('Error fetching bus routes:', error);
      }
  }

  // Populate the routes dropdown based on the fetched data
  function populateRoutes() {
      Object.keys(busData).forEach(route => {
          const option = document.createElement("option");
          option.value = route;
          option.textContent = route;
          busNameSelect.appendChild(option);
      });
  }

  // Initialize data fetching on page load
  async function initialize() {
      await fetchBusStops();
      await fetchBusRoutes();
  }

  initialize();
});
