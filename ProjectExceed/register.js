const form = document.getElementById("dri-form");
const app = document.getElementById("dri-register")
///const cache = [];


function scream(driverName, cargoID, timeStart, source, destination) {
  fetch("", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      driverName: driverName,
      cargoID: cargoID,
      timeStart: timeStart,
      source: source,
      destination: destination
    }),
  }).then((response) => console.log(response));
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  driverName = form.elements["driverName"].value;
  cargoID = form.elements["cargoID"].value;
  timeStart = form.elements["timeStart"].value;
  source = form.elements["source"].value;
  destination = form.elements["destination"].value;
  scream(driverName, cargoID, timeStart, source, destination);
  form.elements["driverName"].value = "";
  form.elements["cargoID"].value = "";
  form.elements["timeStart"].value = "";
  form.elements["source"].value = "";
  form.elements["destination"].value = "";
});
