lastJson = {};
function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

//javascript get key down every 100ms
var timer = setInterval(function(){
    if (keys.size != 0){
        jsonData = {}
        if(keys.has("Semicolon")){
            jsonData['LT'] = 1;
        }
        x = 0;
        y = 0;
        if(keys.has("KeyW")){
            y += -1;
        }
        if(keys.has("KeyS")){
            y += 1;
        }
        if(keys.has("KeyA")){
            x += -1;
        }
        if(keys.has("KeyD")){
            x += 1;
        }
        if(x != 0 || y != 0){
            jsonData['JoystickLeft'] =  [x, y]
        }
        if(JSON.stringify(jsonData) !== '{}' || JSON.stringify(lastJson) !== '{}'){
                var xhr = new XMLHttpRequest();                
                var url = "/commandes";
                xhr.open("POST", url, true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4) {
                        console.log(xhr.status);
                    }
                };
                console.log(jsonData)
                xhr.send(JSON.stringify(jsonData));
            }
            lastJson = jsonData;
    }
}, 100);

var keys = new Set();
window.addEventListener("keydown",
    function(e){
        keys.add(e.code);
    },
false);
window.addEventListener("keyup",
    function(e){
        if(keys.has(e.code)){
            keys.delete(e.code);
        }
    },
false);