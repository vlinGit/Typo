import json
import time
from flask import render_template, make_response
from simple_websocket import Server, ConnectionClosed
from database import Database
from textHelpers import checker
from lobbies import Lobbies

def soloGame(websocket: Server, db: Database, userID):
    start = True
    startTime = 0
    while True:
        data = json.loads(websocket.receive())
        key = data.get('key', '')
        textData = db.getText(userID)

        if start:
            startTime = time.time()
            start = False
        
        if not userID:
            websocket.close()
            response = make_response(render_template('error.html'))
            return response

        payload = checker(db, userID, key, textData, time.time() - startTime)
        websocket.send(payload)
        
def multiGame(websocket: Server, db: Database, lobby: Lobbies, userID, type):
    start = True
    startTime = 0

    while True:
        data = json.loads(websocket.receive())
        lobbyID = data.get("lobbyID")
        curLobby = lobby.lobbies.get(lobbyID)
        
        if not curLobby:
            websocket.send(json.dumps({"match": "timedout"}))
            raise ConnectionClosed
        
        match = data.get("match")
        
        # TODO:
        #   Front end needs a join prompt to enter the lobbyID
        if type == "join":
            joined = lobby.join(lobbyID, websocket)
            if not joined:
                websocket.send(json.dumps({"match": "invalidID"}))
        
        if match == "start":
            if len(curLobby) < 2:
                websocket.send(json.dumps({"match": "noEnemy"}))
        
        # TODO:
        #   Remove the prompt on the front end
        if len(curLobby) == 2:
            websocket.send(json.dumps({"match": "game"}))
            key = data.get('key', '')
            textData = db.getText(userID)
            
            if start:
                startTime = time.time()
                start = False
            
            if not userID:
                websocket.close()
                response = make_response(render_template('error.html'))
                return response

            payload = checker(db, userID, key, textData, time.time() - startTime)
            websocket.send(payload)