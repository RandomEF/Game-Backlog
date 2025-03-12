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
        gamesList.append([gamesResponse[i]["appid"], gamesResponse[i]["name"], imageURL + str(gamesResponse[i]["appid"]) + "/" + gamesResponse[i]["img_icon_url"] + ".jpg",  gamesResponse[i]["playtime_forever"], 0, 0, 0, 0, 0, 0])
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
        return achieved, len(response["achievements"]), round(achieved*100/len(response["achievements"]), 2)

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
            game[7], game[8], game[9] = GetAchievementPercentage(game[0])
        else:
            exceptions.append(game)
    return exceptions

def WriteCSV(library):
    with open("backlog.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["App ID", "Name", "Image URL", "Minutes of Playtime", "Main", "Main + Extra", "Completionist", "Achievements completed", "Achievements total", "Percentage"])
        writer.writerows(library)

def ValidateInput(type):
    passed = False
    while not passed:
        inp = input(type)
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
            game[7], game[8], game[9] = GetAchievementPercentage(game[0])
        else:
            print(game)
            game[4] = ValidateInput("Input Main time:")
            game[5] = ValidateInput("Input Main + Extra time:")
            game[6] = ValidateInput("Input Completionist time:")
            print("NA at any step to set amount of achievements to NA.")
            achieved = ValidateInput("Please enter the amount of achievements achieved: ")
            if achieved == "NA":
                game[7] = "NA"
                game[8] = "NA"
                game[9] = "NA"
                continue
            total = ValidateInput("Please enter the amount of achievements achieved: ")
            if total == "NA":
                game[7] = "NA"
                game[8] = "NA"
                game[9] = "NA"
                continue
            game[7] = int(achieved)
            game[8] = int(total)
            game[9] = round(achieved*100/total, 2)

    WriteCSV(library)

def main():
    #FillFile()
    headers = []
    rows = []
    with open("backlog.csv", "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            if row[9] != "NA":
                row[9] = round(int(row[7])*100/int(row[8]), 2)

            rows.append(row)
    
    with open("backlog.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


if __name__ == '__main__':
    main()
