"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import json
import os.path
import requests
import pandas as pd


def get_data(startYear: int, startDay: int, endYear: int, endDay: int) -> pd.DataFrame:
    """Returns match data within a given interval.

    Args:
        startYear (int): Year of lower interval limit
        startDay (int): Day of lower interval limit
        endYear (int): Year of upper interval limit
        endDay (int): Day of upper interval limit

    Returns:
        Match data (pd.DataFrame) in internal format

    Example:
        df = get_data(2020, 1, 2020, 38)
    """
    dir = f"{os.path.dirname(os.path.abspath(__file__))}/crawled_data"
    filePath = f"{dir}/matches-{startYear}-{startDay}-{endYear}-{endDay}.json"
    if not os.path.exists(filePath):
        fetch_data(startYear, startDay, endYear, endDay, filePath)
    return pd.read_json(filePath)


def api_query(param: str):
    """Sends a request to openligadb.de and parses json response.

    Args:
        param (str): Parameters in the request url [see api.openligadb.de]

    Returns:
        JSON data parsed to python list or dict

    Examples:
        api_query("getavailableleagues")
        api_query("getavailablegroups/bl1/2020")
        api_query("getmatchdata/bl1/2020")
        api_query("getmatchdata/bl1/2020/8")
    """
    assert len(param) > 0, "Specified parameter too short."
    url = f"https://api.openligadb.de/{param}"
    response = requests.get(url, headers={"Accept": "application/json"})
    data = json.loads(response.text)
    return data


def parse_match(match: dict) -> dict:
    """Converts a match from openligadb.de format into internal format.

    Args:
        match (dict): Detailed match data from openligadb

    Returns:
        match (dict): Reduced match data
    """
    goalMinsHome = []
    goalMinsGuest = []
    for g in match["goals"]:
        if g["matchMinute"] is not None:
            if g["scoreTeam1"] != len(goalMinsHome):
                goalMinsHome.append(g["matchMinute"])
            elif g["scoreTeam2"] != len(goalMinsGuest):
                goalMinsGuest.append(g["matchMinute"])
    return {
        "date": match["matchDateTime"],
        "homeClubId": match["team1"]["teamId"],
        "homeClub": match["team1"]["teamName"],
        "guestClubId": match["team2"]["teamId"],
        "guestClub": match["team2"]["teamName"],
        "homeScore": match["matchResults"][0]["pointsTeam1"],
        "guestScore": match["matchResults"][0]["pointsTeam2"],
        "goalMinsHome": goalMinsHome,
        "goalMinsGuest": goalMinsGuest,
        "league": match["leagueShortcut"]
    }


def fetch_data(startYear: int, startDay: int, endYear: int, endDay: int, file: str) -> None:
    """Fetches all bundesliga matches within a given interval.

    Args:
        startYear (int): Year of lower interval limit
        startDay (int): Day of lower interval limit
        endYear (int): Year of upper interval limit
        endDay (int): Day of upper interval limit
        file (str): File path where match data will be saved

    Returns:
        None
    """
    # preconditions: check validity of given time interval
    ### assert startYear > 0 and endYear > 0, "Years must be greater than 0."
    ### assert startYear <= endYear, "Invalid year interval."
    ### assert startDay >= 0 and endDay >= 0, "Days must be positive integers."
    ### assert (startYear < endYear or startDay < endDay), "Invalid day interval."
    # matches is the resulting list of matches
    matches = []
    # crawl match data
    for year in range(startYear, endYear+1):
        for division in ["bl1", "bl2", "bl3"]:
            # parse all finished matches within specified interval
            matchesFetched = api_query(f"getmatchdata/{division}/{year}")
            matchesOfInterest = [
                parse_match(m)
                for m in matchesFetched
                if (year < endYear or m["group"]["groupOrderID"] <= endDay) and m["matchIsFinished"] and m["matchResults"]]
            matches += matchesOfInterest
    # save resulting list of matches as json file
    with open(file, "w") as f:
        json.dump(matches, f)
    return None


def avail_data(details: str = "all") -> list:
    """Returns all bundesliga data available on openligadb.de.

    Args:
        details (str): Defaults to "all", specify "league-only" to skip fetching
                       all available matchdays

    Returns:
        A sorted list of leagues (dicts)
    """
    # get all available leagues of bundesliga
    fetchedLeagues = api_query("getavailableleagues")
    availLeagues = [
        {"ID": l["leagueId"], "season": int(l["leagueSeason"]), "division": l["leagueShortcut"]}
        for l in fetchedLeagues if l["leagueShortcut"] in ["bl1", "bl2", "bl3"]]
    # add available match days to leagues if desired
    if details == "all":
        for league in availLeagues:
            fetchedGroups = api_query(f"getavailablegroups/{league['division']}/{league['season']}")
            league["matchdays"] = [g["groupOrderID"] for g in fetchedGroups]
    return sorted(availLeagues, key=lambda l: l["season"])
