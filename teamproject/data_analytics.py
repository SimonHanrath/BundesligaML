import json
from crawler import fetch_data



"""
The result is a list of matches. A match is a dict of the following structure:
{
    "date": "YYYY-MM-DDTHH:MM:SS",
    "homeClubId": int,
    "homeClub": str,
    "homeScore": int,
    "guestClubId": int,
    "guestClub": str,
    "guestScore": int
}
where "date" specifies the local date and time a match took place,
"homeClubId" and "guestClubId" represent the IDs of the home and visiting club,
"homeClub" and "guestClub" represent the full names of each club,
"homeScore" and "guestScore" represent the final goal score of each club.

ggf. weitere wichtige Daten: Liga; Ort; Tore (Spielminute, Torschütze,
Eigentor?, Strafe?, Verlängerung?); Wetter (von woanders)
"""
filePath = fetch_data(2009,180, 2021,140)
with open(filePath) as file:
    fetchedMatches = json.loads(file.read())

"""
Example:
for match in fetchedMatches:
    print(match["homeScore"])
"""
#testing list of teams in Bundesliga
teams = ["VfL Wolfsburg", "Borussia Dortmund", "1. FC Nürnberg", "Werder Bremen", "Hertha BSC", "1. FSV Mainz 05", "TSG 1899 Hoffenheim", "VfL Bochum", "SC Freiburg", "FC Bayern München", "VfB Stuttgart", "Hamburger SV",
         "Bayer Leverkusen", "Hannover 96", "Eintracht Frankfurt", "1. FC Köln", "Borussia Mönchengladbach", "FC Schalke 04" ]
allTeams = []
dublicate = False
for match in fetchedMatches:
    for team in allTeams:
        if match["homeClub"] == team:
            dublicate = True
            break
        else:
            dublicate = False
    if dublicate == False:
        allTeams.append(match["homeClub"])



# wins by home team
homeWins =0
for match in fetchedMatches:
    if match["homeScore"]>match["guestScore"]:
        homeWins = homeWins+1
print("Heimspieltore: %s" % homeWins)

# wins by guest team
guestWins =0
for match in fetchedMatches:
    if match["homeScore"]<match["guestScore"]:
        guestWins = guestWins+1
print("Gastpieltore: %s" % guestWins)

# draw matches
drawMatches =0
for match in fetchedMatches:
    if match["homeScore"]==match["guestScore"]:
        drawMatches = drawMatches+1
print("Unenschieden Tore: %s" % drawMatches)

# matches of each team as homeClub
def matchResultsHome(homeClub):
    wins = 0
    loses = 0
    draws = 0
    for match in fetchedMatches:
        if match["homeClub"] == homeClub and match["homeScore"] > match["guestScore"]:
            wins = wins + 1
        if match["homeClub"] == homeClub and match["homeScore"] == match["guestScore"]:
            loses = loses + 1
        if match["homeClub"] == homeClub and match["homeScore"] < match["guestScore"]:
            draws = draws + 1

    print(homeClub + " : %s" % wins)
    print(homeClub + " : %s" % loses)
    print(homeClub + " : %s" % draws)

print("machtes of each team as homeClub: ")
for team in allTeams:
    matchResultsHome(team)

# matches of each team as guestClub
def matchResultsGuest(guestClub):
    wins = 0
    loses = 0
    draws = 0
    for match in fetchedMatches:
        if match["guestClub"] == guestClub and match["guestScore"] > match["homeScore"]:
            wins = wins + 1
        if match["guestClub"] == guestClub and match["guestScore"] == match["homeScore"]:
            loses = loses + 1
        if match["guestClub"] == guestClub and match["guestScore"] < match["homeScore"]:
            draws = draws + 1

    print(guestClub + " : %s" % wins)
    print(guestClub + " : %s" % loses)
    print(guestClub + " : %s" % draws)

print("machtes of each team as guestClub: ")
for team in allTeams:
    matchResultsGuest(team)

# against which team were the most wins/loses/draws as homeclub
def specificMatches (homeClub):
    accWins = 0
    accWinsName = ""
    accLoses = 0
    accLosesName = ""
    accDraws = 0
    accDrawsName = ""
    wins = 0
    loses = 0
    draws = 0
    for team in allTeams:
        for match in fetchedMatches:
            if match["homeClub"] == homeClub and match["guestClub"] == team and match["guestScore"] < match["homeScore"]:
                wins = wins +1
            if match["homeClub"] == homeClub and match["guestClub"] == team and match["guestScore"] == match["homeScore"]:
                draws = draws +1
            if match["homeClub"] == homeClub and match["guestClub"] == team and match["guestScore"] > match["homeScore"]:
                loses = loses +1
        if wins > accWins:
            accWins = wins
            accWinsName = team
        wins = 0
        if loses > accLoses:
            accLoses = loses
            accLosesName = team
        loses = 0
        if draws > accDraws:
            accDraws = draws
            accDrawsName = team
        draws = 0

    print("As homeClub " + homeClub + " wins the most times against: " + accWinsName)
    print(homeClub + " has won %s" % accWins + " times against " + accWinsName)
    print("As homeClub " + homeClub + " loses the most times against: " + accLosesName)
    print(homeClub + " has lost %s" % accLoses + " times against " + accLosesName)
    print("As homeClub " + homeClub + " draws the most times against: " + accDrawsName)
    print(homeClub + " draws %s" % accDraws + " times against " + accDrawsName)

# testing with "FC Bayern München"
specificMatches("FC Bayern München")

# against which team were the most wins/loses/draws as homeclub
def specificMatches (guestClub):
    accWins = 0
    accWinsName = ""
    accLoses = 0
    accLosesName = ""
    accDraws = 0
    accDrawsName = ""
    wins = 0
    loses = 0
    draws = 0
    for team in teams:
        for match in fetchedMatches:
            if match["guestClub"] == guestClub and match["homeClub"] == team and match["homeScore"] < match["guestScore"]:
                wins = wins +1
            if match["guestClub"] == guestClub and match["homeClub"] == team and match["homeScore"] == match["guestScore"]:
                draws = draws +1
            if match["guestClub"] == guestClub and match["homeClub"] == team and match["homeScore"] > match["guestScore"]:
                loses = loses +1
        if wins > accWins:
            accWins = wins
            accWinsName = team
        wins = 0
        if loses > accLoses:
            accLoses = loses
            accLosesName = team
        loses = 0
        if draws > accDraws:
            accDraws = draws
            accDrawsName = team
        draws = 0

    print("As guestClub " + guestClub + " wins the most times against: " + accWinsName)
    print(guestClub + " has won %s" % accWins + " times against " + accWinsName)
    print("As guestClub " + guestClub + " loses the most times against: " + accLosesName)
    print(guestClub + " has lost %s" % accLoses + " times against " + accLosesName)
    print("As guestClub " + guestClub + " draws the most times against: " + accDrawsName)
    print(guestClub + " draws %s" % accDraws + " times against " + accDrawsName)

# testing with "FC Bayern München"
specificMatches("FC Bayern München")