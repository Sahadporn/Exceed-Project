const form = document.getElementById("dri-form");
const app = document.getElementById("dri-register")
///const cache = [];


function scream(driver_name, car_id, source, destination, min_temp, max_temp) {
  // Link here!!!
  fetch("http://158.108.182.5:20004/driver_regis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      driver_name: driver_name,
      car_id: car_id,
      source: source,
      // time_start: time_start,
      destination: destination,
      status: 1,
      // waiting for database
      min_temp: min_temp,
      max_temp: max_temp
    }),
  }).then((response) => console.log(response))
    .then(console.log("complete!"))
    .catch((error) => console.log("error", error));
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  driver_name = form.elements["driver_name"].value;
  // console.log(form.elements["driver_name"].value);
  car_id = form.elements["car_id"].value;
  // time_start = form.elements["time_start"].value;
  source = form.elements["source"].value;
  destination = form.elements["destination"].value;
  min_temp = form.elements["min_temp"].value;
  max_temp = form.elements["max_temp"].value;

  scream(driver_name, car_id, source, destination, min_temp, max_temp);
  form.elements["driver_name"].value = "";
  form.elements["car_id"].value = "";
  // form.elements["time_start"].value = "";
  form.elements["source"].value = "";
  form.elements["destination"].value = "";
  form.elements["min_temp"].value = "";
  form.elements["max_temp"].value = "";
});
