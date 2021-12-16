"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import aiohttp
import asyncio
import json
import os.path
import requests
import pandas as pd


def get_data(startYear: int, startDay: int, endYear: int, endDay: int,
             forceUpdate: bool = False) -> pd.DataFrame:
    """Returns match data within a given interval.

    Args:
        startYear (int): Year of lower interval limit
        startDay (int): Day of lower interval limit
        endYear (int): Year of upper interval limit
        endDay (int): Day of upper interval limit
        forceUpdate (bool): TO-DO

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


async def _get_season(session, division: str, season: str):
    url = f"https://api.openligadb.de/getmatchdata/{division}/{season}"
    async with session.get(url, headers={"Accept": "application/json"}) as response:
        data = await response.json()
        return {"division": division, "season": season, "updated": "", "matchData": list(map(parse_match, ld))}


async def fetch_data(leagues: pd.DataFrame) -> None:
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
    async with aiohttp.ClientSession() as session:
        tasks = []
        for l in leagues:
            for d in l["division"]:
                tasks.append(asyncio.create_task(_get_season(session, d, l["season"])))
        leagueData = await asyncio.gather(*tasks)
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/cache/matches.json", "w") as file:
            json.dump(leagueData, file)
    return None


def avail_divisions() -> list:
    """Returns all openligadb shortcuts of bundesliga leagues

    Returns:
        A list of strings (openligadb.de league shortcuts)
    """
    return ["bl1", "bl2", "bl3"]


def avail_data() -> pd.DataFrame:
    """Returns all bundesliga data available on openligadb.de.

    Returns:
        A pandas Dataframe covering all available league seasons and divisions
    """
    #
    # get all available leagues of bundesliga
    fetchedLeagues = api_query("getavailableleagues")
    availLeagues = [
        {"ID": l["leagueId"], "season": int(l["leagueSeason"]), "division": l["leagueShortcut"]}
        for l in fetchedLeagues if l["leagueShortcut"] in avail_divisions()]
    # add available match days to leagues if desired
    # if details == "all":
    #     for league in availLeagues:
    #         fetchedGroups = api_query(f"getavailablegroups/{league['division']}/{league['season']}")
    #         league["matchdays"] = [g["groupOrderID"] for g in fetchedGroups]
    df = pd.DataFrame(availLeagues).groupby('season').agg(list)
    path = f"{os.path.dirname(os.path.abspath(__file__))}/cache/avail_data.csv"
    df.to_csv(path, sep=',', encoding='utf-8')
    return df

x = avail_data()
