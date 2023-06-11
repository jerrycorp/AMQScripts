import time
import json
import sys
import requests
import os
import traceback


class Timer:  # Class for easier ETA printing
    def __init__(self, totalCount=1):  # Give count for how many items will be managed
        self.startTime = time.perf_counter()
        self.stopTime = None
        self.totalCount = totalCount

    def printETA(self, completedCount):
        etaTime = time.perf_counter()
        timeLeft = (etaTime - self.startTime) / completedCount * (self.totalCount - completedCount)
        print(f"Completed: {completedCount}/{self.totalCount}. " +
              f"Estimated time left: {int(timeLeft/60)}min {timeLeft%60:0.2f}s")

    def printCompleted(self):
        if not self.stopTime:
            self.stopTime = time.perf_counter()
        timeUsed = self.stopTime - self.startTime
        print(f"Task completed in {int(timeUsed/60)}min {timeUsed%60:0.2f}s")


def goToDir(dirPath):  # Go to folder for download
    if dirPath == "":  # Just download into current folder
        return True
    try:
        os.mkdir(dirPath)
    except FileExistsError:
        pass
    try:
        os.chdir(dirPath)
    except OSError:
        print("Path bad")
        return False
    return True


def readData(fileName):
    with open(fileName, encoding='utf-8') as f:
        data = json.load(f)
    return data


def filterFileName(word):  # List of banned characters for windows
    bannedCharacters = ["<", ">", ":", "\"", "/", "|", "?", "*"]
    for bannedCharacter in bannedCharacters:
        word = word.replace(bannedCharacter, "")
    return word.strip()  # Remove extra spaces from end and beginning


def songIntoString(song):  # Function for creating file names
    animeName = song["anime"]["romaji"]
    oped = song["type"].replace("Opening", "OP").replace("Ending", "ED").replace("Insert Song", "IN")
    songName = song["name"]
    artistName = song["artist"]
    fileName = f"{animeName} ({oped}) [{songName} - {artistName}]"  # file ending is copied from the downloaded file
    fileName = filterFileName(fileName)
    return fileName


def findUrl(song, fileType):
    priorityList = ["0", "720", "480"] if fileType == "a" else ["720", "480", "0"]
    for priority in priorityList:
        for site in song["urls"]:
            if priority in song["urls"][site]:
                return song["urls"][site][priority]
    print("No media found")
    return None


def download(song, fileType, server):
    if server == "nl"
        url = findUrl(song, fileType).replace("files", "nl")  # Extract url with given file priority
    else:
        url = findUrl(song, fileType)

    if not url:
        print(f"No file found for:")
        print(songIntoString(song))
        return None
    print(f"Downloading : {songIntoString(song)}")
    while True:
        r = requests.get(url, allow_redirects=True)
        if r.ok:  # failed doesn't report ok ?
            break
        else:
            print("Download failed. Trying again")
    with open(songIntoString(song) + "." + url.split(".")[-1], "wb") as out:
        out.write(r.content)


def chooseServer():
    print("Server options: 'nl', 'us'")
    return input("Choose server: ")

def main(data, fileType, server):
    
    print(f"In total {len(data)} songs to download")
    t1 = Timer(len(data))  #Timer for writing ETA
    server = chooseServer()
    for i, song in enumerate(data):
        download(song, fileType, server)
        t1.printETA(i+1)
    t1.printCompleted()
    input("Press any key to end")


def printPlayersChoiseList(players):
    for i, player in enumerate(players):
        print(f"{i}: {player}")


def choosePlayers(data):
    players = []
    for song in data:
        for player in song["players"]:
            if player["name"] not in players:
                players.append(player["name"])
    chosenPlayers = []
    if len(players) == 1:
        return [data[0]["players"][0]["name"]]
    printPlayersChoiseList(players)
    while True:
        print(f"Currently chosen players: {', '.join(chosenPlayers)}")
        player = input("Give player to add or enter to continue: ")
        if player == "" and not players:
            print("give at least one player")
        elif player == "":
            return chosenPlayers
        elif player.isdigit() and 0 <= int(player) < len(players):
            if players[int(player)] not in chosenPlayers:
                chosenPlayers.append(players[int(player)])


def filterList(data):
    newData = []
    while True:
        songs = input("Download (A)ll, (M)issed, (G)uessed: ")
        if len(songs) > 0:
            songs = songs[0].lower()
        if songs == "m":
            players = choosePlayers(data)
            for song in data:
                for player in song["players"]:
                    if player["name"] in players and not player["correct"]:
                        newData.append(song)
            return newData
        elif songs == "g":
            players = choosePlayers(data)
            for song in data:
                for player in song["players"]:
                    if player["name"] in players and player["correct"]:
                        newData.append(song)
            return newData
        else:
            print("Taking all songs")
            return data


if __name__ == "__main__":
    try:
        fileList = sys.argv[1:]  # Take a list of json file as a drag and drop
        data = []
        if not fileList:
            fileList = [input("Give name of file:")]  # If no file given as argument ask for one
        for fileName in fileList:
            data += readData(fileName)
        if goToDir(input("Give a destination directory: ")):  # Setup download directory
            fileType = input("Video or Audio:")  # Only take the first letter
            filetype = fileType or "a"
            filetype = filetype[0].lower()
            data = filterList(data)
            main(data, fileType)
    except Exception as e:
        traceback.print_exc()
        input("")
        raise e
