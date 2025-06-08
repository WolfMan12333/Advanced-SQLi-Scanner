let param = new URLSearchParams(window.location.search).get("id");
document.getElementById("display").innerText = "ID: " + param;

