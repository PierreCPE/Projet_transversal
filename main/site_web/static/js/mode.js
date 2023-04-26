// get all buttons with class choix
var choix = document.getElementsByClassName("choix");
for (var i = 0; i < choix.length; i++) {
  let j = i
  choix[i].addEventListener("click", function () {
    var jsonData = {};
    jsonData["mode"] = j;
    var xhr = new XMLHttpRequest();
    var url = "/commandes";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        console.log(xhr.status);
      }
    };
    console.log(jsonData);
    jsonSend = {};
    jsonSend["config"] = jsonData;
    xhr.send(JSON.stringify(jsonSend));
  });
}
