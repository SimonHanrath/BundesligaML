"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import json, requests, typing
import re

"""
api_query() sends a query to openligadb.de and returns the parsed response.
For example call:
    api_query("getavailablesports")
    api_query("getavailableleagues")
    api_query("getavailablegroups/bl1/2020")
    api_query("getmatchdata/bl1/2020")
    api_query("getmatchdata/bl1/2020/8")
"""
def api_query(param:str):
    url = f"https://api.openligadb.de/{param}"
    response = requests.get(url, headers={"Accept": "application/json"})
    data = json.loads(response.text)
    return data


"""
avail_data() returns all bundesliga data available on openligadb.de. The result
is a (sorted) list of league. A league is a dict of the following structure:
{
    "season": int,
    "division": str,
    "firstMatchday": int,
    "lastMatchday": int
}
where season represents a year and "division" can be one of {"bl1","bl2","bl3"}.
"""
def avail_data() -> list[dict]:
    # get available leagues of bundesliga
    availableLeagues = [{"season":int(l["leagueSeason"]),
        "division":l["leagueShortcut"]}
        for l in api_query("getavailableleagues")
        if l["leagueShortcut"] in ["bl1", "bl2", "bl3"]]
    # add available match days to leagues
    for league in availableLeagues:
        queryStr = f"getavailablegroups/{league['division']}/{league['season']}"
        groups = api_query(f"getavailablegroups" +
            f"/{league['division']}/{league['season']}")
        matchdays = [int(g["groupOrderID"]) for g in groups]
        league["firstMatchday"] = min(matchdays)
        league["lastMatchday"] = max(matchdays)
    availableLeaguesSorted = sorted(availableLeagues, key=lambda l: l["season"])
    return availableLeaguesSorted


"""
parse_match() converts a match from openligadb format into internal format. It
returns a dict of the following structure:
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
"homeScore" and "guestScore" represent the final goals score of each club.
"""
def parse_match(match:dict) -> dict:
    # get final score, which is the last element of the list 'goals'
    # set final score to 0:0 if 'goals' is an empty list
    finalScore = match["goals"][-1:]
    if finalScore:
        homeScore = finalScore[0]["scoreTeam1"]
        guestScore = finalScore[0]["scoreTeam2"]
    else:
        homeScore = 0
        guestScore = 0
    # add current match to the resulting list of matches
    return {
        "date": match["matchDateTime"],
        "homeClubId": match["team1"]["teamId"],
        "homeClub": match["team1"]["teamName"],
        "guestClubId": match["team2"]["teamId"],
        "guestClub": match["team2"]["teamName"],
        "homeScore": homeScore,
        "guestScore": guestScore
    }


"""
fetch_data() fetches match data within a given interval and parses the data by
calling parse_match(). It returns the relative path to a json file, where the
match data is saved. For example call:
filePath = fetch_data(2020,1, 2020,38)
with open(filePath) as file: matches = json.loads(file.read())

ggf. weitere wichtige Daten: Liga; Ort; Tore (Spielminute, Torschütze,
Eigentor?, Strafe?, Verlängerung?); Wetter (von woanders)
"""
def fetch_data(startYear:int, startDay:int, endYear:int, endDay:int) -> str:
    # preconditions: check validity of time span
    assert startYear > 0 and endYear > 0, "Years must be greater than 0."
    assert startYear <= endYear, "Invalid year interval."
    assert startDay >= 0 and endDay >= 0, "Days must be positive integers."
    assert (startYear < endYear or startDay < endDay), "Invalid day interval."
    # matchesOutput is the resulting list of matches
    # filePath is the path to the file containing all fetched data
    matchesOutput = []
    filePath = f"crawled_data/matches-{startYear}-{startDay}-{endYear}-{endDay}.json"
    # check if data has already been crawled before
    try:
        f = open(filePath)
        f.close()
        return filePath
    except IOError:
        pass

    for year in range(startYear, endYear+1):
        for league in ["bl1","bl2","bl3"]: #["bl"+str(n+1) for n in range(3)]
            # parse all finished matches within specified interval
            matchesOfInterest = [parse_match(m)
                for m in api_query(f"getmatchdata/{league}/{year}")
                if (year < endYear or m["group"]["groupOrderID"] <= endDay)
                and m["matchIsFinished"]]
            matchesOutput += matchesOfInterest
    # save resulting list of matches as json file
    with open(filePath, "w") as f:
        json.dump(matchesOutput, f)
    return filePath

    """
    # postconiditions: ensure valid and consistent data format
    #assert all(isinstance(m["date"],str) for m in matchesOutput)
    for m in matchesOutput:
        assert isinstance(m["date"], str)
        assert re.search("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", m["date"]), (
            "Invalid date format")
        assert isinstance(m["homeClub"], str)
        assert isinstance(m["guestClub"], str)
        assert len(m["homeClub"]) > 0 and len(m["guestClub"]) > 0, (
            "Invalid team name")
        assert isinstance(m["homeScore"], int)
        assert isinstance(m["guestScore"], int)
        assert m["homeScore"] >= 0 and m["guestScore"] >= 0, (
            "Invalid number of goals")

        #if len([m for m in matchesFetched if not m["matchIsFinished"]]) > 0:
        #    pass # TO-DO: skip unfinished season?
    """

"""
fetch_seasons() fetches all match data of the last n finished seasons and
returns the relative path to a json file, where the match data is saved.
For example call: fetch_seasons(10)
"""
def fetch_seasons(num:str) -> str:
    pass # TO-DO


print(fetch_data(2020,1, 2020,38))
