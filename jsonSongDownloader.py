import json
import os
import sys
import time
import traceback

import requests


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


def readSongList(fileName):
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


def findUrl(song, fileType, server):
    priorityList = ["0", "720", "480"] if fileType == "a" else ["720", "480", "0"]
    for priority in priorityList:
        for site in song["urls"]:
            if priority in song["urls"][site]:
                url_end = song["urls"][site][priority]
                url = f"https://files.catbox.moe/{url_end}"
                if server == "nl":
                    url.replace("files", "nl")
                return url
    print("No media found")
    return None


def download(song, fileType, server):
    url = findUrl(song, fileType, server)
    if not url:
        print(f"No file found for: {songIntoString(song)}")
        return None
    print(f"Downloading: {songIntoString(song)}")
    while True:
        try:
            r = requests.get(url, allow_redirects=True)
        except KeyboardInterrupt:
            print(f"Download cancelled. Skipping song: {songIntoString(song)}")
            return None
        if r.ok:  # failed doesn't report ok ?
            break
        else:
            try:
                print("Download failed. Trying again in 5 seconds")
                print("Press CTRL+C to cancel")
                time.sleep(5)
                print("Trying again")
            except KeyboardInterrupt:
                print("Choose action:")
                print("s: skip song")
                print("r: retry")
                print("a: retry audio")
                print("v: retry video")
                print("f: retry files")
                choice = input("choice: ")
                if choice.lower() == "":
                    continue
                elif choice.lower()[0] == "s":
                    return None
                elif choice.lower()[0] == "r":
                    continue
                elif choice.lower()[0] == "a":
                    url = findUrl(song, "a", server)
                    continue
                elif choice.lower()[0] == "v":
                    url = findUrl(song, "v", server)
                    continue
                elif choice.lower()[0] == "f":
                    url = findUrl(song, "v", "files")
                    continue
                else:
                    continue
    with open(songIntoString(song) + "." + url.split(".")[-1], "wb") as out:
        out.write(r.content)


def chooseServer():
    print("Server options: 'nl', 'files'")
    return input("Choose server: ")


def downloadSongs(songList, fileType):
    print(f"In total {len(songList)} songs to download")
    t1 = Timer(len(songList))  # Timer for writing ETA
    server = chooseServer()
    for i, song in enumerate(songList):
        download(song, fileType, server)
        t1.printETA(i+1)
    t1.printCompleted()
    input("Press any key to end")


def printPlayersChoiceList(players):
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
    printPlayersChoiceList(players)
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
        songs = input("Download All, Missed, Guessed: ")
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


def main():
    try:
        fileList = sys.argv[1:]  # Take a list of json file as a drag and drop
        songList = []
        if not fileList:
            fileList = [input("Give name of file:")]  # If no file given as argument ask for one
        for fileName in fileList:
            songList += readSongList(fileName)
        if goToDir(input("Give a destination directory: ")):  # Setup download directory
            fileType = input("Video or Audio: ")  # Only take the first letter
            filetype = fileType or "a"
            filetype = filetype[0].lower()
            songList = filterList(songList)
            downloadSongs(songList, fileType)
    except Exception as e:
        traceback.print_exc()
        input("")
        raise e


if __name__ == "__main__":
    main()
