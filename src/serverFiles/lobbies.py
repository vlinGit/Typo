import random
from simple_websocket import Server

class Lobbies:
    # lobby -> [lobbyInfo, host, joined]
    def __init__(self):
        self.lobbies: dict[str, list] = {}
        self.socketMap: dict[str, Server] = {}
    
    def start(self, conn, text):
        id = str(random.getrandbits(64))
        while self.lobbies.get(id):
            id = random.getrandbits(64)
        
        lobby = [text, conn]
        self.lobbies[id] = lobby
        
        return id

    def join(self, id, conn):
        curLobby: list = self.lobbies.get(id, None)
        
        if not curLobby:
            return None
        
        text = curLobby[0]
        curLobby.append(conn)
        self.lobbies[id] = curLobby
        
        return text

    def delete(self, id):
        self.lobbies.pop(id)
            
    