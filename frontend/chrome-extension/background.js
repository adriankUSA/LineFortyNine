let previousTimes = {}; // Store the previous ETA keyed by bus ID
let timer = 0; // Timer to track seconds since the last alert
let alertActive = false; // Flag to indicate if an alert is active

// Function to fetch ETA and next stop for the selected bus
async function fetchNextStopAndEstimatedTime(vehicleId) {
    const response = await fetch(`http://127.0.0.1:5000/api/next-stop/${vehicleId}`);
    if (!response.ok) throw new Error('Failed to fetch data');
    return await response.json(); // Assumes response JSON includes `next_stop` and `estimated_time_to_next_stop_minutes`
}

// Check ETA every minute
setInterval(async () => {
    const selectedBusId = localStorage.getItem('selectedBusId'); // Get selected bus ID from local storage
    if (!selectedBusId) return;

    const nextStopData = await fetchNextStopAndEstimatedTime(selectedBusId);
    const newEta = nextStopData.estimated_time_to_next_stop_minutes;
    const nextStop = nextStopData.next_stop;

    // If the ETA has decreased, show notification with updated info
    if (previousTimes[selectedBusId] && newEta < previousTimes[selectedBusId]) {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: '/frontend/chrome-extension/images/line49Logo.png',
            title: 'Bus ETA Alert',
            message: `The arrival time for bus ${selectedBusId} has decreased to ${newEta} minutes. Next Stop: ${nextStop}.`
        });
        
        // Reset timer and log alert
        alertActive = true;
        timer = 0; // Reset timer
        console.log(`Alert set for bus ${selectedBusId}. Timer reset.`); // Log alert
    }

    previousTimes[selectedBusId] = newEta; // Update stored ETA
}, 60000);

// Timer function to log elapsed time
setInterval(() => {
    if (alertActive) {
        timer++; // Increment the timer every minute
        console.log(`Time since last alert: ${timer} minute(s)`);
    }
}, 60000);
