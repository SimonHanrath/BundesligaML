"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import json, requests, typing

"""
fetch_data() fetches match data in a given interval
For example call fetch_data(2020,1,2020,8)
For example call fetch_data(2020,0,0,0)
The result is a list of matches. A match is a dictionary structured as follows:
{
    "date": "YYYY-MM-DDTHH:MM:SSZ",
    "homeClub": str,
    "visitingClub": str,
    "goalsHomeClub": int,
    "goalsVisitingClub": int
}

ggf. weitere wichtige Daten:
• Liga
• Ort
• Tore: Spielminute, Torschütze, Eigentor?, Strafe?, Verlängerung?
• Wetter (von woanders)?
"""
def fetch_data(startYear:int, startDay:int, endYear:int, endDay:int) -> None:
    # matchesOutput is the resulting list of matches
    matchesOutput = []

    # check validity of time span, return empty list if invalid time span
    if (startYear > endYear) or (startYear == endYear and startDay > endDay):
        print("Invalid time span. No data fetched.")
        return None

    # specify parameters for api fetches:
    # apiScheme defines the fundamental query mode
    # leaguesOfInterest specifys a list of league short names
    # see: https://www.openligadb.de/Datenhaushalt/
    # yearsOfInterest is a list of all selected years
    apiScheme = "https://api.openligadb.de/getmatchdata/"
    yearsOfInterest = range(startYear, endYear+1)
    leaguesOfInterest = ["bl"+str(n+1) for n in range(3)]

    # loop over years, leagues and fetch matches
    for year in yearsOfInterest:
        for league in leaguesOfInterest:
            # fetch JSON data from openligadb.de
            url = apiScheme + league + "/" + str(year)
            response = requests.get(url, headers={"Accept": "application/json"})
            matchesFetched = json.loads(response.text)
            print("Fetching " + url)

            # check if season is finished
            matchesUnfinished = [m for m in matchesFetched if not m["matchIsFinished"]]
            if (len(matchesUnfinished) > 0):
                pass # skip season? TO-DO

            # only consider finished matches within specified interval
            matchesOfInterest = [m for m in matchesFetched if m["matchIsFinished"] and not(year == endYear and m["group"]["groupOrderID"] > endDay)]

            # convert input JSON from openligadb to internal format
            # only loop over finished matches
            for match in matchesOfInterest:
                # get final score, which is the last element of 'goals' list
                goalsFinalScore = match["goals"][-1:]
                # if 'goals' list is empty, set final score to 0:0
                if not(goalsFinalScore):
                    goalsHomeClub = 0
                    goalsVisitingClub = 0
                else:
                    goalsHomeClub = goalsFinalScore[0]["scoreTeam1"]
                    goalsVisitingClub = goalsFinalScore[0]["scoreTeam2"]
                # append a new JSON-object which represents a match
                matchesOutput.append({
                    "date": match["matchDateTimeUTC"],
                    "homeClub": match["team1"]["shortName"],
                    "visitingClub": match["team2"]["shortName"],
                    "goalsHomeClub": goalsHomeClub,
                    "goalsVisitingClub": goalsVisitingClub
                })

    # write result to file
    with open("matches.json", "w") as outfile:
        json.dump(matchesOutput, outfile)

    return None

fetch_data(2020,1,2022,1)
