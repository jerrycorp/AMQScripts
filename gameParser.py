import json
import sys


def readData(fileName):
    with open(fileName) as f:
        data = json.load(f)
    return data


def separateSessions(gameData):
    previousNumber = -1
    games = []
    for song in gameData:
        if song["songNumber"] != previousNumber+1:
            games.append([])
        previousNumber = song["songNumber"]
        games[-1].append(song)
    return games


def getRig(gameData):
    rig = {}
    for player in gameData[0]["players"]:
        rig[player["name"]] = 0
    for song in gameData:
        for player in song["fromList"]:
            rig[player["name"]] +=1
    return rig


def getScore(gameData):
    score = {}
    for player in gameData[-1]["players"]:
        score[player["name"]] = player["score"]
    return score


def getPlayers(gameData):
    players = []
    for player in gameData[-1]["players"]:
        players.append(player["name"])
    return players


def writeGameSummary(gameData):
    print()
    print("Game with players:", ", ".join(getPlayers(gameData)))
    print(f"Played rounds {len(gameData)}")
    print(f"Score: {getScore(gameData)}")
    print(f"Rig: {getRig(gameData)}")


def parseJsonFile(fileName):
    data = readData(fileName)
    games = separateSessions(data)
    print(f"Json file has {len(games)} games")
    for game in games:
        writeGameSummary(game)


def main(fileNames):
    if fileNames:
        for fileName in fileNames:
            parseJsonFile(fileName)
    else:
        fileName = input("Give name of file:")
        parseJsonFile(fileName)
    input("Press enter to close")


if __name__ == "__main__":
    main(sys.argv[1:])
