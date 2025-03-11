from howlongtobeatpy import HowLongToBeat as hltb
import requests
from localVars import steamID, key
from json import loads
import csv

idAdd = f"&steamid={steamID}"
steamURL = "http://api.steampowered.com/"
libraryURL = f"IPlayerService/GetOwnedGames/v0001/?key={key}&include_appinfo=true&format=json" + idAdd
userStatsURL = f"ISteamUserStats/GetPlayerAchievements/v0001/?key={key}&appid="
imageURL = "http://media.steampowered.com/steamcommunity/public/images/apps/"

def GetSteamLibrary():
    response = loads(requests.get(steamURL+libraryURL).text)
    gamesList = []
    gamesResponse = response["response"]["games"]
    for i in range(response["response"]["game_count"]):
        gamesList.append([gamesResponse[i]["appid"], gamesResponse[i]["name"], imageURL + str(gamesResponse[i]["appid"]) + "/" + gamesResponse[i]["img_icon_url"] + ".jpg",  gamesResponse[i]["playtime_forever"], 0, 0, 0, 0])
    return gamesList

def GetAchievementPercentage(game):
    url = steamURL+userStatsURL+str(game)+idAdd
    response = requests.get(url).text
    response = loads(response)["playerstats"]
    if "error" in response:
        return "NA"
    elif "achievements" not in response:
        return "NA"
    else:
        achieved = 0
        for achievement in response["achievements"]:
            if achievement["achieved"] == 1:
                achieved += 1
        return str(achieved) + "/" + str(len(response["achievements"])) 

def FillGameData(library):
    exceptions = []
    for game in library:
        game[1] = game[1].replace('™', '').replace('®', '')
        results = hltb().search(game[1], similarity_case_sensitive=False)
        if results is not None and len(results) > 0:
            best = max(results, key=lambda elem: elem.similarity)
            game[4] = best.main_story
            game[5] = best.main_extra
            game[6] = best.completionist
            game[7] = GetAchievementPercentage(game[0])
        else:
            exceptions.append(game)
    return exceptions

def WriteCSV(library):
    with open("backlog.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["App ID", "Name", "Image URL", "Minutes of Playtime", "Main", "Main + Extra", "Completionist", "Achievements"])
        writer.writerows(library)

def ValidateInput(type):
    passed = False
    while not passed:
        inp = input(f"Input {type} time: ")
        if inp == "NA":
            return inp
        try:
            float(inp)
        except ValueError:
            print("Wrong format")
        else:
            return float(inp)

def FillFile():
    library = GetSteamLibrary()
    exceptions = FillGameData(library)
    for game in exceptions:
        # temp = game
        results = hltb().search(game[1], similarity_case_sensitive=False)
        if results is not None and len(results) > 0:
            best = max(results, key=lambda elem: elem.similarity)
            game[4] = best.main_story
            game[5] = best.main_extra
            game[6] = best.completionist
            game[7] = GetAchievementPercentage(game[0])
        else:
            print(game)
            game[4] = ValidateInput("Main")
            game[5] = ValidateInput("Main + Extra")
            game[6] = ValidateInput("Completionist")
            print("NA at any step to set amount of achievements to NA.")
            achieved = input("Please enter the amount of achievements achieved: ")
            if achieved == "NA":
                game[7] = "NA"
                continue
            total = input("Please enter the amount of achievements achieved: ")
            if total == "NA":
                game[7] = "NA"
                continue
            game[7] = str(achieved) + "/" + str(total)
    WriteCSV(library)

def main():
    FillFile()

if __name__ == '__main__':
    main()
