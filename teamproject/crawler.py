"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import json, os, requests, typing
import pandas as pd

def api_query(param:str):
    """
    Sends a request to openligadb.de and parses json response.
        Parameters:
            param (str): Parameters in the request url [see api.openligadb.de]
        Returns:
            data (list, dict): JSON data parsed to python list (or dict)
        Examples:
            api_query("getavailableleagues")
            api_query("getavailablegroups/bl1/2020")
            api_query("getmatchdata/bl1/2020")
            api_query("getmatchdata/bl1/2020/8")
            More see
    """
    assert len(param) > 0, "Specified parameter too short."
    url = f"https://api.openligadb.de/{param}"
    response = requests.get(url, headers={"Accept": "application/json"})
    data = json.loads(response.text)
    return data


def avail_data(details:str = "all") -> list[dict]:
    """
    Returns all bundesliga data available on openligadb.de.
        Parameters:
            details (str): Specify "league-only" to skip fetching matchdays
        Returns:
            data (list[dict]): A sorted list of leagues (dicts)
    """
    # get all available leagues of bundesliga
    fetchedLeagues = api_query("getavailableleagues")
    availLeagues = [{"ID": l["leagueID"], "season": int(l["leagueSeason"]),
        "division": l["leagueShortcut"]} for league in fetchedLeagues
        if league["leagueShortcut"] in ["bl1", "bl2", "bl3"]]
    # add available match days to leagues if desired
    if details == "all":
        for league in availLeagues:
            fetchedGroups = api_query("getavailablegroups/" +
                f"{league['division']}/{league['season']}")
            league["matchdays"] = [g["groupOrderID"] for g in fetchedGroups]
    return sorted(availableLeagues, key=lambda l: l["season"])


def parse_match(match:dict) -> dict:
    """
    Converts a match from openligadb.de format into internal format.
        Parameters:
            match (dict): Detailed match data from openligadb
        Returns:
            match (dict): Reduced match data
    """
    return {
        "date": match["matchDateTime"],
        "homeClubId": match["team1"]["teamId"],
        "homeClub": match["team1"]["teamName"],
        "guestClubId": match["team2"]["teamId"],
        "guestClub": match["team2"]["teamName"],
        "homeScore": match["matchResults"][0]["pointsTeam1"],
        "guestScore": match["matchResults"][0]["pointsTeam2"]
    }


def fetch_data(startYear:int, startDay:int, endYear:int, endDay:int) -> str:
    """
    Fetches all bundesliga matches within a given interval.
        Parameters:
            startYear (int): Year of lower interval limit
            startDay (int): Day of lower interval limit
            endYear (int): Year of upper interval limit
            endDay (int): Day of upper interval limit
        Returns:
            filePath (str): Path to json file containing all fetched data
        Example:
            filePath = fetch_data(2020,1, 2020,38)
            with open(filePath) as file: matches = json.loads(file.read())
            matchesDF = pd.DataFrame.read_json(filePath)
    """
    # preconditions: check validity of given time interval
    assert startYear > 0 and endYear > 0, "Years must be greater than 0."
    assert startYear <= endYear, "Invalid year interval."
    assert startDay >= 0 and endDay >= 0, "Days must be positive integers."
    assert (startYear < endYear or startDay < endDay), "Invalid day interval."
    # matches is the resulting list of matches
    matches = []
    filePath = f"{os.path.dirname(__file__)}/crawled_data/" + (
        f"matches-{startYear}-{startDay}-{endYear}-{endDay}.json")
    # check if data has already been crawled before
    try:
        f = open(filePath)
        f.close()
        return filePath
    except IOError:
        pass

    for year in range(startYear, endYear+1):
        for division in ["bl1","bl2","bl3"]:
            # parse all finished matches within specified interval
            matchesFetched = api_query(f"getmatchdata/{division}/{year}")
            matchesOfInterest = [parse_match(m) for m in matchesFetched
                if (year < endYear or m["group"]["groupOrderID"] <= endDay)
                and m["matchIsFinished"]]
            matches += matchesOfInterest
    # save resulting list of matches as json file
    with open(filePath, "w") as f:
        json.dump(matches, f)
    return filePath


def fetch_seasons(numSeasons:int) -> str:
    """
    Fetches all bundesliga matches of the last finished seasons.
        Parameters:
            numSeasons (int): Number of seasons that should be fetched
        Returns:
            filePath (str): Path to json file containing all fetched data
    """
    latestLeague = avail_data("leagues-only")[-1:]
    assert latestLeague, "No available leagues."
    return fetch_data(latestLeague-numSeasons-1, 1, latestLeague, 0)


# ggf. weitere wichtige Daten: Liga; Ort; Tore (Spielminute, Torschütze,
# Eigentor?, Strafe?, Verlängerung?); Wetter (von woanders)

#print(fetch_data(2020,1, 2020,38))
#print(avail_data())
