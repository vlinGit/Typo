from pymongo import MongoClient

class Database():
    def __init__(self, mongoType: str):
        self.mongoClient: MongoClient = MongoClient(mongoType)
        self.database = self.mongoClient["db"]
        self.textData = self.database["text"]
    
    # insert into the text entry of a user
    def insertText(self, userID: str, text: dict):
        if self.textData.find_one({"userID": userID}):
            self.textData.update_one({"userID": userID}, {"$set": {"text": text}})
        else:
            self.textData.insert_one({"userID": userID, "text": text})

    # updates the text entry of a user
    def updateText(self, userID: str, text: dict):
        if self.textData.find_one({"userID": userID}):
            self.textData.update_one({"userID": userID}, {"$set": {"text": text}})
        else:
            self.insertText(userID, text)
    
    def deleteText(self, userID: str):
        if self.textData.find_one({"userID": userID}):
            self.textData.delete_one({"userID": userID}) 
    
    # Returns the entire entry in the text collection
    def getUser(self, userID: str) -> dict:
        if self.textData.find_one({"userID": userID}):
            return self.textData.find_one({"userID": userID})

        return {}
    
    def getText(self, userID: str) -> dict:
        userData = self.getUser(userID)
        
        if userData:
            return userData['text']
        
        return ''