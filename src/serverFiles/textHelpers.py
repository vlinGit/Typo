import json
import requests
from database import Database

def charDict(string):
    charDict = {}
    for i in range(len(string)):
        charDict[str(i)] = 0
    
    return charDict

# RATE LIMIT OF 180 REQUESTS PER MINUTE
def generateText():
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            jsonData = response.json()
            return {'content': jsonData['content'], 'author': jsonData['author'], 'length': int(jsonData['length']),
                    'curLetter': 0, 'charDict': charDict(jsonData['content'])}
        print("Getting text did not return 200")
        return {}
    except:
        print("Getting text failed, resorting to default")
        content = "Hello world, programmed to work but not to feel."
        return {'content': content, 'author': 'Robot', 'length': len(content),
                'curLetter': 0, 'charDict': charDict(content)}

# Pass in the time in minutes
def formatTime(time: float) -> str:
    timeSec = time*60
    seconds = timeSec % (24*3600)
    seconds = seconds % 3600
    minutes = seconds // 60
    
    return "%02d:%02d" % (minutes, seconds)

def formatDecimal(percentage: float) -> str:
    return str(round(percentage, 2))

# Gross WPM: (All typed entries/5)/time(min)
# Net WPM: Gross WPM - (Uncorrected errors/time(min))
# TODO:
#   implement Net WPM (gross does not account for errors)
def calculate(length: int, time: float, wrongCount: int, uncorrectedCount: int):
    timeMin = time/60
    acc = (1-(wrongCount/length))*100
    try:
        gross = (length/5)/timeMin
        net = gross - (uncorrectedCount/timeMin)
        
        payload = {"net": formatDecimal(net), "accurancy": formatDecimal(acc), "time": formatTime(timeMin)}
        if net >= 300:
            payload["message"] = "Did you cheat?"
        
        return payload
    except:
        return {"net": "&infin;", "accurancy": formatDecimal(acc), "time": formatTime(timeMin), "message": "Did you cheat?"}

# The values stored are: 0 = wrong, 1 = correct
# Calling values 'correct' as it just makes more sense when reading the code
def uncorrectedCount(charDict):
    uncorrectedCount = 0
    for correct in charDict.values():
        if not correct:
            uncorrectedCount+=1

    return uncorrectedCount

# sets the character as correct (1) in the charDict
def setCorrect(db: Database, textData, curLetter, length, userID):
    charDict = textData.get("charDict")
    charDict[str(curLetter)] = 1
    textData["charDict"] = charDict
    textData['curLetter'] = min(length, curLetter + 1)
    db.insertText(userID, textData)

# sets the character as incorrect (0) in the charDict
def setIncorrect(db: Database, textData, curLetter, length, userID):
    charDict = textData.get("charDict")
    charDict[str(curLetter)] = 0
    textData["charDict"] = charDict
    textData["wrong"] = textData.get("wrong", 0) + 1
    db.insertText(userID, textData)

def checker(db: Database, userID: str, key: str, textData, time=0):
    content = textData.get('content', '')
    curLetter = textData.get('curLetter', 0)
    length = textData.get('length', 0)
    
    if curLetter >= length-1:
        setCorrect(db, textData, curLetter, length, userID)
        textData = db.getText(userID)
        charDict = textData.get("charDict")
        stats = calculate(length, time, textData.get("wrong", 0), uncorrectedCount(charDict))
        toSend = json.dumps({"match":"game", "status": "done", "correct": True, "currentLetter": curLetter, "stats": stats, "length":length, "progress": 100})
    else:
        rightKey = content[curLetter]
        progress = "%02d" % (((curLetter+1)/length)*100)
        if key == rightKey:
            # Sets the current character as correct in the charDict
            setCorrect(db, textData, curLetter, length, userID)
            
            toSend = json.dumps({"match":"game", "status": "inprogress", "correct": True, "currentLetter": curLetter, "length": length, "progress": progress})
        else:
            toSend = {"match":"game", "status": "inprogress", "correct": False, "actual": rightKey, "currentLetter": curLetter, "length": length, "progress": progress}
            
            if (key == "Backspace"):
                toSend["backspace"] = True
                textData['curLetter'] = max(0, curLetter - 1)
            else:
                textData['curLetter'] = min(length, curLetter + 1)
            
            # Sets the current character as incorrect in charDict
            setIncorrect(db, textData, curLetter, length, userID)
            
            toSend = json.dumps(toSend)

    return toSend