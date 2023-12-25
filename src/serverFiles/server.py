import json
import secrets
import time
from flask import Flask, render_template, send_file, make_response, redirect, url_for, request
from flask_sock import Sock
from simple_websocket import Server, ConnectionClosed
from textHelpers import *
from lobbyHelper import *
from wsHelpers import *
from database import Database
from lobbies import Lobbies

app = Flask(__name__, template_folder="../../templates")
sock = Sock(app)
db = Database("localhost")
lobby = Lobbies()

@app.route("/")
def index():
    userID = request.cookies.get('userID', secrets.token_urlsafe(16))
    response = make_response(render_template('index.html'))
    response.set_cookie('userID', userID)
    return response

@app.route("/game")
def game():
    type = request.args.get("type", "solo")
    userID = request.cookies.get('userID')
    textData = generateText()
    db.insertText(userID, textData)
    response = make_response(render_template('type.html', textList=textData.get('content').split(' '), author=textData.get('author'), length=textData.get('length'), percentage=0))
    response.set_cookie('userID', userID)
    response.set_cookie('type', type)
    
    return response

@app.route("/host")
def host():
    userID = request.cookies.get("userID")
    textData = generateText()
    lobbyID = lobby.start(userID, textData)
    print(lobbyID)
    response = make_response(render_template("host.html", lobbyID=lobbyID))
    response.set_cookie("userID", userID)
    
    return response

# TODO:
#   MAKE SURE TO HANDLE INJECTION ATTACKS
#   use .isdigit(), if it's false than raise an error
@app.route("/join", methods=['GET', 'POST'])
def join():
    userID = request.cookies.get("userID")
    
    if request.method == "GET":
        response = make_response(render_template("join.html"))
        response.set_cookie("userID", userID)
        
        return response
    
    lobbyID = request.json.get("id")
    lobby.join(lobbyID, userID)
    # make a redirect to game page
    return "temporary return"
    

@app.route("/startGame", methods=['GET', 'POST'])
def startGame():
    if request.method == "POST":
        lobbyID = request.headers.get("lobbyID", "")
        curLobby = lobby.lobbies.get(lobbyID, None)
        if curLobby:
            if len(curLobby) > 0:
                return make_response(json.dumps({"match": "start", "url": "/game"}))
            return make_response(json.dumps({"match": "notReady"}))
        return make_response(json.dumps({"match": "invalidID"}))

@app.route("/static/<filepath>")
def staticFile(filepath):
    print("retrieving:", filepath)
    filepath = filepath.replace('/', '')
    
    if filepath.endswith('.css'):
        mime = 'text/css'
    elif filepath.endswith('.js'):
        mime = 'text/javascript'
    
    request = send_file(f'../../static/{filepath}', mimetype=mime)    
    return request

# TODO:
# if value for 'type' is host/join, set up the lobby
@sock.route("/websocket")
def ws(websocket: Server):
    userID = request.cookies.get('userID')
    type = request.cookies.get("type")

    try:
        if type == "solo":
            soloGame(websocket, db, userID)
        else:
            multiGame(websocket, db, lobby, userID, type)
    except ConnectionClosed:
        db.deleteText(userID)

# use celery
@sock.route("/timer")
def timer(websocket: Server):
    lobbyID = ""
    counter = time.time()
    try:
        while True:
            data = json.loads(websocket.receive())
            lobbyID = data.get("lobbyID")
            
            if lobbyID and (time.time() - counter == 10):
                websocket.send(json.dumps({"match": "timerDone"}))
                break
        raise ConnectionClosed
    except ConnectionClosed:
        if lobbyID:
            lobby.delete(lobbyID)

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = '8000'
    
    app.run(debug=True, host=HOST, port=PORT)
    sock.init_app(app)
