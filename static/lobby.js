const timer = new WebSocket('ws://' + window.location.host + '/timer');
const xml = new XMLHttpRequest();

timer.onopen = function() {
    console.log("called");
    const lobbyID = document.getElementById("lobbyID").innerHTML;
    timer.send(JSON.stringify({lobbyID: lobbyID}));
}

function startGame(){
    const lobbyID = document.getElementById("lobbyID").innerHTML;
    const error = document.getElementById("error");
    const popup = document.getElementById("popup");

    xml.onreadystatechange = function(){
        if (this.readyState == 4 && this.status == 200){
            const data = JSON.parse(xml.response);
            
            if (data.match == "start"){
                window.location.href = data.url;
            }else{
                handleError(data);
            }
        }
    };
    xml.open("POST", "/startGame");
    xml.setRequestHeader("lobbyID", lobbyID);
    xml.send();
}

function errorMessage(error){
    return "<p id='error'>" + error + "</p>";
}

function handleError(message){
    const popup = document.getElementById("popup");
    const error = document.getElementById("error");
    
    var errorText = "";
    if (message.match == "timerDone"){
        errorText = "The lobby has expired";
    }else if(message.match == "notReady"){
        errorText = "There is no opponent";
    }else if (message.match == "invalidID"){
        errorText = "The lobby no longer exists"
    }
    
    const errorTag = errorMessage(errorText);
    if (!error){
        popup.innerHTML += errorTag
    }else{
        error.innerHTML = errorTag
    }
}

timer.onmessage = function(timerMessage){
    const message = JSON.parse(timerMessage.data);
    
    if (message.match == "temp"){
        console.log("start success");
    }else{
        handleError(message);
    }
}