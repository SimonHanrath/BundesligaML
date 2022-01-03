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

cache_path = f'{os.path.dirname(os.path.abspath(__file__))}/cache'

def get_data(fromSeason: int, fromMatchDay: int, toSeason: int, toMatchDay: int,
             forceUpdate: bool = False) -> pd.DataFrame:
    """Returns match data within a given interval.

    Args:
        fromSeason (int): Year of lower interval limit
        fromMatchDay (int): Day of lower interval limit
        toSeason (int): Year of upper interval limit
        toMatchDay (int): Day of upper interval limit
        forceUpdate (bool): TO-DO

    Returns:
        Match data (pd.DataFrame) in internal format

    Example:
        df = get_data(2020, 1, 2020, 38)
    """
    avail = avail_data()
    # filter out unavailable seasons
    seasons = avail[avail['season'].isin(range(fromSeason, toSeason + 1))]
    # filter out cached seasons (if forceUpdate flag is not set)
    fetch = seasons
    if not forceUpdate:
        fetch = fetch[~fetch['cached']]
    fetch = fetch.explode('division')[['season', 'division']]
    asyncio.run(fetch_data(fetch.to_dict('records')))
    # read and concat match data from cache
    frames = []
    for season in seasons['season'].unique().tolist():
        df = pd.read_csv(f'{cache_path}/{season}.csv', parse_dates=['dateTime', 'dateTimeUTC'])
        if season == fromSeason:
            df = df[df['matchDay'] >= fromMatchDay]
        if season == toSeason:
            df = df[df['matchDay'] <= toMatchDay]
        frames.append(df)
    matchData = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return matchData


async def fetch_data(leagues: list):
    """
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for l in leagues:
            params = {'division': l['division'], 'season': l['season']}
            tasks.append(asyncio.ensure_future(fetch_query(session, params)))
        data = await asyncio.gather(*tasks)
        for key, val in groupby(data, key=lambda d: d['params']['season']):
            frames = map(lambda d: parse_league(d['response']), val)
            matchData = pd.concat(frames)
            matchData.to_csv(f'{cache_path}/{key}.csv', index=False)
            # update avail_data cache
            filePath = f'{cache_path}/avail_data.csv'
            avail = pd.read_csv(filePath)
            avail.loc[avail['season'] == key, ['matchDays', 'cached', 'lastUpdate']] = [matchData['matchDay'].max(), True, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
            avail.to_csv(filePath, index=False)


async def fetch_query(session, params) -> dict:
    """Fetches all bundesliga matches within a given interval.

    Args:

    Returns:
        None
    """
    paramStr = '/'.join(map(str, params.values()))
    url = f'https://api.openligadb.de/getmatchdata/{paramStr}'
    async with session.get(url) as resp:
        print(f'Fetching {url}')
        response = await resp.json()
        return {'params': params, 'response': response}


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
    matches.rename({'matchDateTime': 'dateTime', 'leagueSeason': 'season', 'leagueShortcut': 'division', 'matchDateTimeUTC': 'dateTimeUTC', 'group.groupOrderID': 'matchDay', 'team1.teamId': 'homeID', 'team1.teamName': 'homeName', 'team1.teamIconUrl': 'homeIcon', 'team2.teamId': 'guestID', 'team2.teamName': 'guestName', 'team2.teamIconUrl': 'guestIcon', 'team2': 'guestTeam'}, axis=1, inplace=True)
    matches['dateTime'] = pd.to_datetime(matches['dateTime'])
    matches['dateTimeUTC'] = pd.to_datetime(matches['dateTimeUTC'])
    if 'location.locationID' in matches.columns:
        matches.rename({'location.locationID': 'locID', 'location.locationCity': 'locCity', 'location.locationStadium': 'locStadium'}, axis=1, inplace=True)
        matches = matches.astype({'locID': 'Int64'})
    else:
        matches[['locID', 'locCity', 'locStadium']] = None
    matches = matches[['season', 'division', 'dateTime', 'dateTimeUTC', 'matchDay', 'homeID', 'homeName', 'homeIcon', 'guestID', 'guestName', 'guestIcon', 'homeScore', 'guestScore', 'locID', 'locCity', 'locStadium']]
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
    leagues = filter(lambda l: l['season'] >= 2005, leagues)
    avail = pd.DataFrame(leagues).sort_values(['season', 'division'])
    avail = avail.groupby('season').agg(list)
    avail.reset_index(level=0, inplace=True)
    avail[['matchDays', 'cached', 'lastUpdate']] = [38, False, None]
    filePath = f'{cache_path}/avail_data.csv'
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
