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
        word = word.replace(bannedCharacter, " ")
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


def download(song, fileType):
    url = findUrl(song, fileType)  # Extract url with given file priority
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


def main(data, fileType):
    t1 = Timer(len(data))  #Timer for writing ETA
    for i, song in enumerate(data):
        download(song, fileType)
        t1.printETA(i+1)
    t1.printCompleted()
    input("Press any key to end")


if __name__ == "__main__":
    try:
        fileList = sys.argv[1:]  # Take a list of json file as a drag and drop
        data = []
        if not fileList:
            fileList = [input("Give name of file:")]  # If no file given as argument ask for one
        for fileName in fileList:
            data += readData(fileName)
        if goToDir(input("Give a destination directory: ")):  # Setup download directory
            fileType = input("Video or Audio:")[0].lower()  # Only take the first letter
            if fileType:
                main(data, fileType)
            else:
                print("No file type given")
                time.sleep(5)
    except Exception as e:
        traceback.print_exc()
        input("")
        raise e
