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
    15: "RIGHT"
};

function gamepadHandler(event, connecting) {
    var gamepad = event.gamepad;

    if (connecting) {
        gamepadIndex = gamepad.index;
        console.log("Manette connectée");
    } else {
        console.log("Manette déconnectée");
    }

    setInterval(function() {
        var gamepad = navigator.getGamepads()[gamepadIndex];
        if (gamepad) {
            var jsonData = {};
            // Détecter les mouvements des deux joysticks
            var x_left = round(gamepad.axes[0],1);
            var y_left = round(gamepad.axes[1],1);
            var x_right = round(gamepad.axes[2],1);
            var y_right = round(gamepad.axes[3],1);
            if (Math.abs(x_left) > 0 || Math.abs(y_left) > 0){
                jsonData['JoystickLeft'] =  x_left +';' + y_left
            } 
            if (Math.abs(x_right) > 0 || Math.abs(y_right) > 0){
                jsonData['JoystickRight'] =  x_right +';' + x_right
            }
            for (var i = 0; i < gamepad.buttons.length; i++) {
                if (gamepad.buttons[i].pressed) {
                    var buttonName = buttonMap[i];
                    if(gamepad.buttons[i].value > 0){
                        jsonData[buttonName] = gamepad.buttons[i].value
                    }
                }
            }
            if(JSON.stringify(jsonData) !== '{}'){
                console.log(jsonData)
            }
        }
    }, 100);
}

window.addEventListener("gamepadconnected", function(event) {
    document.getElementById('menu_left').setAttribute("mode",1) 
    gamepadHandler(event, true);
});

window.addEventListener("gamepaddisconnected", function(event) {
    document.getElementById('menu_left').setAttribute("mode",0)   
    gamepadHandler(event, false);
});

function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}