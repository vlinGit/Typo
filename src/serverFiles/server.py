import json
import secrets
import time
from flask import Flask, render_template, send_file, make_response, Response, request
from flask_sock import Sock
from simple_websocket import Server, ConnectionClosed
from ws import *
from textHelpers import *
from database import Database

app = Flask(__name__, template_folder="../../templates")
sock = Sock(app)
db = Database("localhost")

# TODO:
# use mongo to store user tokens, should avoid the worry of running of threads in gunicorn

#gen a cookie token for identification
@app.route("/")
def index():
    userID = request.cookies.get('userID', secrets.token_urlsafe(16))
    textData = generateText()
    #textData = {"content": '1', "author": "Me", "length": 1, "curLetter": 0, 'charDict': {'0': 0}}
    db.insertText(userID, textData)
    response = make_response(render_template('index.html', textList=textData.get('content').split(' '), author=textData.get('author'), length=textData.get('length'), percentage=0))
    response.set_cookie('userID', userID)
    return response

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
# Create a class to manage connections
# Current all connections are independent
@sock.route("/websocket")
def ws(websocket: Server):
    userID = request.cookies.get('userID')
    try:
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
    except ConnectionClosed:
        db.deleteText(userID)

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = '8000'
    app.run(debug=True, host=HOST, port=PORT)
    sock.init_app(app)
    