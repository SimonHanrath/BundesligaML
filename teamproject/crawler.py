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
from ast import literal_eval
from datetime import datetime
from itertools import groupby

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
    avail = avail_data()
    # filter out unavailable seasons
    seasons = avail[avail['season'].isin(range(startYear, endYear + 1))]
    # filter out cached seasons (if forceUpdate flag is not set)
    fetch = seasons
    if not forceUpdate:
        fetch = fetch[~fetch['cached']]
    fetch = fetch.explode('division')[['season', 'division']]
    asyncio.run(fetch_data(fetch.to_dict('records')))
    # read and concat match data from cache
    frames = []
    for season in seasons['season'].unique().tolist():
        df = pd.read_csv(f'{cache_path()}/{season}.csv')
        if season == startYear:
            df = df[df['matchDay'] >= startDay]
        if season == endYear:
            df = df[df['matchDay'] <= endDay]
        frames.append(df)
    matches = pd.concat(frames) if frames else pd.DataFrame()
    return matches


async def fetch_data(leagues: list):
    """
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for l in leagues:
            tasks.append(asyncio.ensure_future(fetch_league(session, l['season'], l['division'])))
        data = await asyncio.gather(*tasks)
        for key, val in groupby(data, key=lambda d: d['season']):
            frames = list(map(lambda d: parse_league(d['response']), val))
            matchData = pd.concat(frames)
            matchData.to_csv(f'{cache_path()}/{key}.csv', index=False)
            # update avail_data cache
            filePath = f'{cache_path()}/avail_data.csv'
            avail = pd.read_csv(filePath)
            avail.loc[avail['season'] == key, ['matchDays', 'cached', 'updated']] = [matchData['matchDay'].max(), True, str(datetime.now())]
            avail.to_csv(filePath, index=False)


async def fetch_league(session, season, division) -> dict:
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

    url = f'https://api.openligadb.de/getmatchdata/{division}/{season}'
    async with session.get(url) as resp:
        print(f'Fetching {url}')
        response = await resp.json()
        return {'season': season, 'division': division, 'response': response}


def parse_league(data: list) -> pd.DataFrame:
    """Converts a match from openligadb.de format into internal format.

    Args:
        data (list): Detailed match data from openligadb

    Returns:
        match (pd.DataFrame): Reduced match data
    """
    matches = pd.json_normalize(data)
    matches = matches[matches['matchIsFinished'] & (len(matches['matchResults']) > 0)]
    matches['homeScore'] = matches['matchResults'].apply(lambda l: l[0]['pointsTeam1'])
    matches['guestScore'] = matches['matchResults'].apply(lambda l: l[0]['pointsTeam2'])
    matches.rename({'matchDateTime': 'date', 'leagueSeason': 'season', 'leagueShortcut': 'division', 'matchDateTimeUTC': 'dateUTC', 'group.groupOrderID': 'matchDay', 'team1.teamId': 'homeID', 'team1.teamName': 'homeName', 'team1.teamIconUrl': 'homeIcon', 'team2.teamId': 'guestID', 'team2.teamName': 'guestName', 'team2.teamIconUrl': 'guestIcon', 'team2': 'guestTeam'}, axis=1, inplace=True)
    if 'location.locationID' in matches.columns:
        matches.rename({'location.locationID': 'locID', 'location.locationCity': 'locCity', 'location.locationStadium': 'locStadium'}, axis=1, inplace=True)
        matches = matches.astype({'locID': 'Int64'})
    else:
        matches[['locID', 'locCity', 'locStadium']] = None
    matches = matches[['season', 'division', 'date', 'dateUTC', 'matchDay', 'homeID', 'homeName', 'homeIcon', 'guestID', 'guestName', 'guestIcon', 'homeScore', 'guestScore', 'locID', 'locCity', 'locStadium']]
    return matches


def avail_data() -> pd.DataFrame:
    """Returns all bundesliga data available on openligadb.de.

    Returns:
        A pandas Dataframe covering all available league seasons and divisions
    """
    url = 'https://api.openligadb.de/getavailableleagues'
    response = requests.get(url, headers={'Accept': 'application/json'})
    data = json.loads(response.text)
    leagues = [
        {'IDs': l['leagueId'], 'season': int(l['leagueSeason']), 'division': l['leagueShortcut']}
        for l in data if l['leagueShortcut'] in avail_divisions()]
    leagues = list(filter(lambda l: l['season'] >= 2005, leagues))
    avail = pd.DataFrame(leagues).sort_values(['season', 'division'])
    avail = avail.groupby('season').agg(list)
    avail.reset_index(level=0, inplace=True)
    avail[['matchDays', 'cached', 'updated']] = [38, False, None]
    filePath = f'{cache_path()}/avail_data.csv'
    if os.path.exists(filePath):
        cache = pd.read_csv(filePath)
        cache['division'] = cache['division'].apply(literal_eval)
        avail = pd.concat([avail[~avail.season.isin(cache.season)], cache])
    avail.to_csv(filePath, index=False)
    return avail


def avail_divisions() -> list:
    """Returns all openligadb shortcuts of bundesliga leagues

    Returns:
        A list of strings (openligadb.de league shortcuts)
    """
    return ['bl1', 'bl2', 'bl3']


def cache_path() -> str:
    """Returns the absolute path of the cache directory

    Returns:
        A string containing the absolute path of the cache directory
    """
    return f'{os.path.dirname(os.path.abspath(__file__))}/cache'
