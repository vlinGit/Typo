"use strict";

const ws = new WebSocket('ws://' + window.location.host + '/websocket');
const http = new XMLHttpRequest();
var isFocused = false;
var words = document.getElementsByClassName('word');

function updateText(curIndex, progress, backspace=false){
    var letter = document.getElementsByTagName("letter")[curIndex];
    var progressDiv = document.getElementById("progress");
    var progressBar = document.getElementsByTagName("progressBar")[0];
    if (letter){
        if (backspace){
            var pre = document.getElementsByTagName("letter")[curIndex-1];
            letter.id = curIndex;
            pre.id = "current";
        }else{
            var next = document.getElementsByTagName("letter")[curIndex+1];
            letter.id = "complete";
            next.id = "current";
        }
        progressDiv.innerHTML = progress;
        progressBar.style.transform = "scaleX(100)";
    }
}

function wrongText(curIndex){
    var letter = document.getElementsByTagName("letter")[curIndex];
    const text = document.getElementById("textbox");
    
    if (letter){
        letter.id = "wrong";
        document.getElementById(curIndex + 1).id = "current";
    }

    text.classList.add("wrong");
    text.addEventListener("animationend", () => {
        text.classList.remove("wrong");
    })
}

function restart(){
    location.reload();
}

function done(netWPM, acc, time){
    const restart =  document.getElementById("restart");
    var stats = document.getElementById("stats");
    var accurancy = document.createElement("p");
    var netSpeed = document.createElement("p");
    var timeTaken = document.createElement("p");
    
    accurancy.innerHTML = "Accuracy: " + acc + "%";
    netSpeed.innerHTML = "WPM: " + netWPM;
    timeTaken.innerHTML = "Time (m:s): " + time;
    stats.appendChild(accurancy);
    stats.appendChild(netSpeed);
    stats.appendChild(timeTaken);
    restart.style.visibility = "visible";
}

window.addEventListener("keypress", function(e){
    if (e.key != "Enter"){
        ws.send(JSON.stringify({ key: e.key }));
    }
});

window.addEventListener("keydown", function(e){
    if (e.key == "Backspace"){
        const toDelete = document.getElementById("current");
        ws.send(JSON.stringify({ key: "Backspace", toDelete: toDelete}))
    }
});

ws.onmessage = function(wsMessage){
    const message = JSON.parse(wsMessage.data);
    const correct = message.correct;
    const status = message.status;
    const cur = message.currentLetter;
    const stats = message.stats;
    const backspace = message.backspace;
    const progress = message.progress;

    console.log(progress);
    if (status == "done"){
        updateText(cur, progress);
        done(stats.net, stats.accurancy, stats.time);
        if (stats.message) console.log("%c" + stats.message, "color:red; font-size:50px;")
    }else if (correct || backspace){
        updateText(cur, progress, backspace);
    }else{
        wrongText(cur);
    }
}