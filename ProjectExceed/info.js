// const url = 'http://158.108.182.5:20004/temp_his?car_id=1';
const url33 = 'http://158.108.182.5:20004/driver_update';

function send1() {
    console.log("send");
    fetch(url33,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ car_id: "1", status: 1 })
        }).then((response) => console.log(response)).then((a) => window.location.reload());
    // console.log("Update status conplete!!!");
}

let button1 = document.getElementById("click1");

button1.addEventListener("click", (event) => {
    event.preventDefault();
    send1();
    //   window.location.reload();
});



function send2() {
    console.log("send");
    fetch(url33,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ car_id: "1", status: 2 })
        }).then((response) => console.log(response)).then((a) => window.location.reload());
    // console.log("Update status conplete!!!");
}

let button2 = document.getElementById("click2");

button2.addEventListener("click", (event) => {
    event.preventDefault();
    send2();
    //   window.location.reload();
});
