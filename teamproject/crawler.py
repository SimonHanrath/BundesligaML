"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import json, re, requests, typing

"""
fetch_data() fetches match data within a given interval. The resulting is a list
matches. A match is a dictionary of the following structure:
{
    "date": "YYYY-MM-DDTHH:MM:SSZ",
    "homeClub": str,
    "visitingClub": str,
    "goalsHomeClub": int,
    "goalsVisitingClub": int
}
where "date" specifies the date and time a match took place in UTC as indicated
by letter "Z" (zero meridian) at the end of the string,
"homeClub" and "visitingClub" represent the names of the home and visiting club,
"goalsHomeClub" and "goalsVisitingClub" represent the final goals score of each
club.
For example call:
data = fetch_data(2020,1,2020,8)
with open("matches.json", "w") as file:
    json.dump(data, file)

ggf. weitere wichtige Daten:
• Liga
• Ort
• Tore: Spielminute, Torschütze, Eigentor?, Strafe?, Verlängerung?
• Wetter (von woanders)
"""
def fetch_data(startYear:int, startDay:int, endYear:int, endDay:int) -> list:
    # preconditions: check validity of time span
    assert startYear <= endYear, "Invalid year interval"
    assert (startYear < endYear or startDay < endDay), "Invalid day interval"

    # matchesOutput is the resulting list of matches
    matchesOutput = []

    # specify parameters for api fetches:
    # apiScheme determines the fundamental query mode
    # leaguesOfInterest is a list of str representing league identifiers
    # (see: https://www.openligadb.de/Datenhaushalt)
    # yearsOfInterest is a list of int representing years
    apiScheme = "https://api.openligadb.de/getmatchdata/"
    yearsOfInterest = range(startYear, endYear+1)
    leaguesOfInterest = ["bl"+str(n+1) for n in range(3)]

    for year in yearsOfInterest:
        for league in leaguesOfInterest:
            # fetch json data from openligadb.de
            url = apiScheme + league + "/" + str(year)
            response = requests.get(url, headers={"Accept": "application/json"})
            matchesFetched = json.loads(response.text)
            print("Fetching " + url)

            # check if season contains unfinished matches
            if len([m for m in matchesFetched if not m["matchIsFinished"]]) > 0:
                pass # TO-DO: skip unfinished season?

            # only consider finished matches within specified interval
            matchesOfInterest = [m for m in matchesFetched
                if m["matchIsFinished"]
                and not(year==endYear and m["group"]["groupOrderID"] > endDay)]

            # convert openligadb json format to internal format
            for match in matchesOfInterest:
                # get final score, which is the last element of the list 'goals'
                # set final score to 0:0 if 'goals' is an empty list
                scoreFinal = match["goals"][-1:]
                if scoreFinal:
                    scoreHome = scoreFinal[0]["scoreTeam1"]
                    scoreVisiting = scoreFinal[0]["scoreTeam2"]
                else:
                    scoreHome = 0
                    scoreVisiting = 0
                # add current match to the resulting list of matches
                matchesOutput.append({
                    "date": match["matchDateTimeUTC"],
                    "homeClub": match["team1"]["teamName"],
                    "visitingClub": match["team2"]["teamName"],
                    "goalsHomeClub": scoreHome,
                    "goalsVisitingClub": scoreVisiting
                })

    # postconiditions: ensure valid and consistent data format
    #assert all(isinstance(m["date"],str) for m in matchesOutput)
    for m in matchesOutput:
        assert isinstance(m["date"], str)
        assert re.search("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", m["date"]), (
            "Invalid date format")
        assert isinstance(m["homeClub"], str)
        assert isinstance(m["visitingClub"], str)
        assert len(m["homeClub"]) > 0 and len(m["visitingClub"]) > 0, (
            "Invalid team name")
        assert isinstance(m["goalsHomeClub"], int)
        assert isinstance(m["goalsVisitingClub"], int)
        assert m["goalsHomeClub"] >= 0 and m["goalsVisitingClub"] >= 0, (
            "Invalid number of goals")

    # return resulting list of matches
    return matchesOutput


"""
data = fetch_data(2020,1,2020,8)
with open("matches.json", "w") as file:
    json.dump(data, file)
"""
