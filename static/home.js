"user strict";
const request = new XMLHttpRequest();

function solo(){
    location.href = "game?type=solo"
}

function host(){
    location.href = "game?type=host"
}

function join(){
    location.href = "game?type=join"
}