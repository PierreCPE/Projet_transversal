var gamepadIndex = -1;
var buttonMap = {
  0: "A",
  1: "B",
  2: "X",
  3: "Y",
  4: "LB",
  5: "RB",
  6: "LT",
  7: "RT",
  8: "Affichage",
  9: "Menu",
  10: "LeftStick",
  11: "RightStick",
  12: "UP",
  13: "DOWN",
  14: "LEFT",
  15: "RIGHT",
};

lastJson = {};

function gamepadHandler(event, connecting) {
  var gamepad = event.gamepad;

  if (connecting) {
    gamepadIndex = gamepad.index;
    console.log("Manette connectée");
  } else {
    console.log("Manette déconnectée");
  }
  setInterval(function () {
    var gamepad = navigator.getGamepads()[gamepadIndex];
    if (gamepad) {
      var jsonData = {};
      // Détecter les mouvements des deux joysticks
      var x_left = round(gamepad.axes[0], 1);
      var y_left = round(gamepad.axes[1], 1);
      var x_right = round(gamepad.axes[2], 1);
      var y_right = round(gamepad.axes[3], 1);
      if (window.location.hash == "#Controlleur") {
        left_element = document.getElementById("GP_LeftStick");
        right_element = document.getElementById("GP_RightStick");
        if (left_element != null) {
          left_element.setAttribute("cx", 113 + 10 * x_left + "");
          left_element.setAttribute("cy", 160 + 10 * y_left + "");
        }
        if (right_element != null) {
          right_element.setAttribute("cx", 278 + 10 * x_right + "");
          right_element.setAttribute("cy", 238 + 10 * y_right + "");
        }

        left_element_zoom = document.getElementById("GP_LeftStick_Zoom");
        right_element_zoom = document.getElementById("GP_RightStick_Zoom");
        if (left_element_zoom != null) {
          left_element_zoom.setAttribute("cx", 78.5 * x_left + "");
          left_element_zoom.setAttribute("cy", 78.5 * y_left + "");
          document
            .getElementById("left_x")
            .setAttribute("x", 78.5 * x_left + "");
          document.getElementById("left_x").innerHTML = round(x_left, 2) + "";
          document
            .getElementById("left_y")
            .setAttribute("y", 78.5 * y_left + "");
          document.getElementById("left_y").innerHTML = round(y_left, 2) + "";
        }
        if (right_element_zoom != null) {
          right_element_zoom.setAttribute("cx", 78.5 * x_right + "");
          right_element_zoom.setAttribute("cy", 78.5 * y_right + "");
        }
      }
      if (Math.abs(x_left) > 0.1 || Math.abs(y_left) > 0.1) {
        jsonData["JoystickLeft"] = [x_left, y_left];
      }
      if (Math.abs(x_right) > 0.1 || Math.abs(y_right) > 0.1) {
        jsonData["JoystickRight"] = [x_right, y_right];
      }
      for (var i = 0; i < gamepad.buttons.length; i++) {
        var buttonName = buttonMap[i];

        if (window.location.hash == "#Controlleur") {
          path_element = document.getElementById("GP_" + buttonName);
          if (path_element != null) {
            path_element.setAttribute(
              "fill",
              "rgba(0,0,0," + gamepad.buttons[i].value + ")"
            );
          }
        }
        if (gamepad.buttons[i].pressed) {
          if (gamepad.buttons[i].value > 0) {
            jsonData[buttonName] = gamepad.buttons[i].value;
          }
        }
      }
      if (
        JSON.stringify(jsonData) !== "{}" ||
        JSON.stringify(lastJson) !== "{}"
      ) {
        var xhr = new XMLHttpRequest();
        var url = "/commandes";
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
          if (xhr.readyState === 4 && xhr.status === 200) {
            // Le serveur a répondu avec succès
          }
        };
        console.log(jsonData);
        jsonSend = {};
        jsonSend["control"] = jsonData;
        xhr.send(JSON.stringify(jsonSend));
      }
      lastJson = jsonData;
    }
  }, 100);
}

window.addEventListener("gamepadconnected", function (event) {
  document.getElementById("menu_left").setAttribute("mode", 1);
  gamepadHandler(event, true);
});

window.addEventListener("gamepaddisconnected", function (event) {
  document.getElementById("menu_left").setAttribute("mode", 0);
  gamepadHandler(event, false);
});
