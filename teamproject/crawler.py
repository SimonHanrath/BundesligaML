"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import json, requests, typing

"""
fetch_data() fetches match data in a given interval
For example call fetch_data(2020,1,2020,8)
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
        return matchesOutput

    # specify parameters for api fetches:
    # apiScheme defines the fundamental query scheme
    # leaguesOfInterest specifys a list of league short names
    # see: https://www.openligadb.de/Datenhaushalt/
    # yearsOfInterest is a list of all selected years
    apiScheme = "https://api.openligadb.de/getmatchdata/"
    leaguesOfInterest = ["bl"+str(n+1) for n in range(3)]
    yearsOfInterest = range(startYear, endYear+1)
    day = startDay

    # loop over leagues, years, days and fetch data records
    for league in leaguesOfInterest:
        for year in yearsOfInterest:
            # loop over days until empty fetch or specified endDay reached
            while not(year == endYear and day > endDay):
                # fetch JSON data from openligadb.de
                url = apiScheme + league + "/" + str(year) + "/" + str(day)
                response = requests.get(url,headers={"Accept":"application/json"})
                matchesFetched = json.loads(response.text)
                print("Fetching " + url)

                # break loop if there is no data for a day
                # (continue with next year)
                if len(matchesFetched) == 0:
                    break
                # day increment after every api fetch
                day += 1

                # convert input JSON from openligadb to internal format
                for match in matchesFetched:
                    # get final score, which is the last element of 'goals' list
                    goalsFinalScore = match["goals"][-1:]
                    # if 'goals' list is empty, set final score 0:0
                    if not(goalsFinalScore):
                        goalsHomeClub = 0
                        goalsVisitingClub = 0
                    else:
                        goalsHomeClub = goalsFinalScore[0]["scoreTeam1"]
                        goalsVisitingClub = goalsFinalScore[0]["scoreTeam2"]
                    # create a new JSON-object which represents a match
                    matchesOutput.append({
                        "date": match["matchDateTimeUTC"],
                        "homeClub": match["team1"]["shortName"],
                        "visitingClub": match["team2"]["shortName"],
                        "goalsHomeClub": goalsHomeClub,
                        "goalsVisitingClub": goalsVisitingClub
                    })

            # having fetched a year, reset day counter to the first day
            day = 1

    # write result to file
    with open("data-placeholder.json", "w") as outfile:
        json.dump(matchesOutput, outfile)

    return None
