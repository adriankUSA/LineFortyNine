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