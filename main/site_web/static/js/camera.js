// get element with detection_color_flag id
var detection_color_flag = document.getElementById("detection_color_flag");
// element is a checkbox, intercept the change event
detection_color_flag.addEventListener("change", function () {
  var jsonData = {};
  jsonData["detection_contour"] = detection_color_flag.checked;
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

var point_simulation_flag = document.getElementById("point_simulation_flag");
// element is a checkbox, intercept the change event
point_simulation_flag.addEventListener("change", function () {
  var jsonData = {};
  jsonData["point_simulation"] = point_simulation_flag.checked;
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

var capture_color_flag = document.getElementById("capture_color_flag");
// When click on button send tag
capture_color_flag.addEventListener("onclick", function () {
  var jsonData = {};
  jsonData["capture_color"] = true;
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

// get elements with input tag in element point_simulation_data_inputs id
var point_simulation_data_inputs = document.getElementById("point_simulation_data_inputs").getElementsByTagName("input");
for (var i = 0; i < point_simulation_data_inputs.length; i++) {
    // element is a numbers, intercept the change event
    point_simulation_data_inputs[i].addEventListener("change", function () {
        send_simulation_point_data();
    });
}

// fonction qui envoyer les données de simulation
function send_simulation_point_data() {
    var jsonData = {};
    jsonData["point_simulation_data"] = [0,0,0];
    for (var i = 0; i < point_simulation_data_inputs.length; i++) {
        jsonData["point_simulation_data"][i] = parseFloat(point_simulation_data_inputs[i].value);
    }
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
}

