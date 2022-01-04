"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""
import aiohttp
import asyncio
import os.path
import pandas as pd
from ast import literal_eval
from datetime import datetime
from itertools import groupby


g_cache_path = f'{os.path.dirname(os.path.abspath(__file__))}/cache'
g_divisions = ['bl1', 'bl2', 'bl3']
g_season_lower_limit = 2005


def get_data(fromSeason: int, fromMatchDay: int, toSeason: int, toMatchDay: int,
             forceUpdate: bool = False) -> pd.DataFrame:
    """Returns match data within a given interval.

    Args:
        fromSeason (int): Year of lower interval limit
        fromMatchDay (int): Day of lower interval limit
        toSeason (int): Year of upper interval limit
        toMatchDay (int): Day of upper interval limit
        forceUpdate (bool): Force re-caching of seasons within interval

    Returns:
        Match data as pd.DataFrame (or empty pd.DataFrame)

    Example:
        df = get_data(2020, 1, 2020, 38)
    """
    avail = load_cache_index()
    # filter out unavailable and cached seasons
    seasons = avail[avail['season'].isin(range(fromSeason, toSeason + 1))].copy()
    seasonList = seasons['season'].unique().tolist()
    if not forceUpdate:
        seasons = seasons[~seasons['cached']]
    # fetch data if necessary
    seasons['action'] = 'getmatchdata'
    leagues = seasons.explode('division')[['action', 'division', 'season']]
    responses = asyncio.run(fetch_queries(leagues.to_dict('records')))
    for key, val in groupby(responses, key=lambda d: d['params']['season']):
        frames = map(lambda d: parse_league(d['response']), val)
        store_season(key, pd.concat(frames))
    # assemble interval from cache
    frames = []
    for season in seasonList:
        df = pd.read_csv(f'{g_cache_path}/matches-{season}.csv', parse_dates=['datetime', 'datetimeUTC'])
        if season == fromSeason:
            df = df[df['matchday'] >= fromMatchDay]
        if season == toSeason:
            df = df[df['matchday'] <= toMatchDay]
        frames.append(df)
    matchData = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return matchData


def parse_league(data: list) -> pd.DataFrame:
    """Converts a match from openligadb.de format into internal format.

    Args:
        data (list): Detailed match data from openligadb

    Returns:
        match (pd.DataFrame): Reduced match data
    """
    matches = pd.json_normalize(data)
    matches['homeScore'] = matches['matchResults'].apply(lambda l: l[0]['pointsTeam1'] if l else None).astype('Int64')
    matches['guestScore'] = matches['matchResults'].apply(lambda l: l[0]['pointsTeam2'] if l else None).astype('Int64')
    matches.rename({'matchDateTime': 'datetime', 'leagueSeason': 'season', 'leagueShortcut': 'division', 'matchDateTimeUTC': 'datetimeUTC', 'matchIsFinished': 'finished', 'group.groupOrderID': 'matchday', 'team1.teamId': 'homeID', 'team1.teamName': 'homeName', 'team1.teamIconUrl': 'homeIcon', 'team2.teamId': 'guestID', 'team2.teamName': 'guestName', 'team2.teamIconUrl': 'guestIcon', 'team2': 'guestTeam'}, axis=1, inplace=True)
    matches['datetime'] = pd.to_datetime(matches['datetime'])
    matches['datetimeUTC'] = pd.to_datetime(matches['datetimeUTC'])
    if 'location.locationID' in matches.columns:
        matches.rename({'location.locationID': 'locID', 'location.locationCity': 'locCity', 'location.locationStadium': 'locStadium'}, axis=1, inplace=True)
        matches = matches.astype({'locID': 'Int64'})
    else:
        matches[['locID', 'locCity', 'locStadium']] = None
    matches = matches[['season', 'division', 'datetime', 'datetimeUTC', 'matchday', 'homeID', 'homeName', 'homeIcon', 'guestID', 'guestName', 'guestIcon', 'finished', 'homeScore', 'guestScore', 'locID', 'locCity', 'locStadium']]
    return matches


def store_season(season: int, matches: pd.DataFrame):
    """
    """
    matches.reset_index(inplace=True)
    matches.drop(matches[~matches['finished']].index, axis=0, inplace=True)
    matches.drop('finished', axis=1, inplace=True)
    matches.to_csv(f'{g_cache_path}/matches-{season}.csv', index=False)
    avail = load_cache_index()
    avail.loc[avail['season'] == season, ['cachedMatchdays', 'cached', 'cachedDatetime']] = [matches['matchday'].max(), True, str(datetime.now())]
    avail.to_csv(f'{g_cache_path}/index.csv', index=False)


def fetch_avail_leagues() -> pd.DataFrame:
    """
    """
    responses = asyncio.run(fetch_queries([{'action': 'getavailableleagues'}]))
    leagues = [{'IDs': l['leagueId'], 'season': int(l['leagueSeason']), 'division': l['leagueShortcut']} for l in responses[0]['response'] if l['leagueShortcut'] in g_divisions]
    leagues = filter(lambda l: l['season'] >= g_season_lower_limit, leagues)
    avail = pd.DataFrame(leagues).sort_values(['season', 'division'])
    avail = avail.groupby('season').agg(list).reset_index()
    avail[['availMatchdays', 'cached', 'cachedMatchdays', 'cachedDatetime']] = [None, False, None, None]
    cache = load_cache_index()
    if not cache.empty:
        avail = pd.concat([avail[~avail.season.isin(cache.season)], cache])
    avail = avail.astype({'cachedMatchdays': 'Int64'})
    avail.to_csv(f'{g_cache_path}/index.csv', index=False)
    return avail


def fetch_avail_match_days():
    """
    """
    avail = load_cache_index()
    leagues = avail.explode('division')
    leagues = leagues[['division', 'season']]
    leagues.insert(0, 'action', 'getavailablegroups')
    queries = leagues.to_dict('records')
    responses = asyncio.run(fetch_queries(queries))
    data = [{'season': l['params']['season'], 'availMatchdays': max(l['response'], key=lambda x:x['groupOrderID'])['groupOrderID']} for l in responses]
    df = pd.DataFrame(data).groupby('season').agg(max)
    df['availMatchdays'] = df['availMatchdays'].astype('Int64')
    avail.set_index('season', inplace=True)
    avail.update(df)
    avail.to_csv(f'{g_cache_path}/index.csv')


def fetch_next_matches():
    """
    """
    avail = load_cache_index()
    current = avail.explode('division')
    current = current[['division', 'season']]
    currentSeason = current['season'].max()
    current = current[current['season'] == currentSeason]
    current.insert(0, 'action', 'getmatchdata')
    queries = current.to_dict('records')
    responses = asyncio.run(fetch_queries(queries))
    df = pd.concat(map(lambda d: parse_league(d['response']), responses))
    store_season(currentSeason, df.copy())
    df = df[df['datetimeUTC'] >= pd.Timestamp.utcnow()]
    df = df[df['datetimeUTC'] == df['datetimeUTC'].min()]
    df.to_csv(f'{g_cache_path}/next_matches.csv', index=False)


async def fetch_queries(queries: list) -> list:
    """
    """
    async with aiohttp.ClientSession() as session:
        tasks = map(lambda params: asyncio.ensure_future(query(session, params)), queries)
        responses = await asyncio.gather(*tasks)
        return responses


async def query(session, params: dict) -> dict:
    """Fetches all bundesliga matches within a given interval.

    Args:

    Returns:
        None
    """
    paramStr = '/'.join(map(str, params.values()))
    url = f'https://api.openligadb.de/{paramStr}'
    async with session.get(url) as resp:
        # print(f'Fetching {url}')
        response = await resp.json()
        return {'params': params, 'response': response}


def load_cache_index(fetchIfEmpty: bool = True) -> pd.DataFrame:
    """
    """
    path = f'{g_cache_path}/index.csv'
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['division'] = df['division'].apply(literal_eval)
        df = df.astype({'cachedMatchdays': 'Int64'})
    elif fetchIfEmpty:
        fetch_avail_leagues()
        df = load_cache_index()
    else:
        df = pd.DataFrame()
    return df
