const form = document.getElementById("dri-form");
const app = document.getElementById("dri-register")
///const cache = [];


function scream(driver_name, cargo_id, source, destination) {
  // Link here!!!
  fetch("http://158.108.182.5:20004/driver/regis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      driver_name: driver_name,
      cargo_id: cargo_id,
      source: source,
      // time_start: time_start,
      destination: destination,
      status: 1
    }),
  }).then((response) => console.log(response))
    .catch((error) => console.log("error", error));
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  driver_name = form.elements["driver_name"].value;
  // console.log(form.elements["driver_name"].value);
  cargo_id = form.elements["cargo_id"].value;
  // time_start = form.elements["time_start"].value;
  source = form.elements["source"].value;
  destination = form.elements["destination"].value;
  scream(driver_name, cargo_id, source, destination);
  form.elements["driver_name"].value = "";
  form.elements["cargo_id"].value = "";
  // form.elements["time_start"].value = "";
  form.elements["source"].value = "";
  form.elements["destination"].value = "";
});
