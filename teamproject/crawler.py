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


g_divisions = ['bl1', 'bl2', 'bl3']
g_season_lower_limit = 2005
g_cache_path = f'{os.path.dirname(os.path.abspath(__file__))}/cache'
if not os.path.exists(g_cache_path):
    os.mkdir(g_cache_path)


def get_data(fromSeason: int, fromMatchday: int, toSeason: int,
             toMatchday: int, forceUpdate: bool = False) -> pd.DataFrame:
    """Returns match data within a given interval.

    Args:
        fromSeason (int): Season of lower interval limit
        fromMatchday (int): Day of lower interval limit
        toSeason (int): Season of upper interval limit
        toMatchday (int): Day of upper interval limit
        forceUpdate (bool): Force re-caching of seasons in interval

    Returns:
        Match data as pd.DataFrame (can be empty)
    """
    avail = load_cache_index()
    # filter out unavailable and cached seasons
    seasons = avail[avail['season'].isin(range(fromSeason, toSeason+1))].copy()
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
    matchData = pd.DataFrame()
    for season in seasonList:
        path = f'{g_cache_path}/matches_{season}.csv'
        df = pd.read_csv(path, parse_dates=['datetime', 'datetimeUTC'])
        df['locID'] = df['locID'].astype('Int64')
        if season == fromSeason:
            df = df[df['matchday'] >= fromMatchday]
        if season == toSeason:
            df = df[df['matchday'] <= toMatchday]
        frames.append(df)
    matchData = pd.concat(frames, ignore_index=True)
    return matchData


def parse_league(data: list) -> pd.DataFrame:
    """Converts match data (of a league) into internal format.

    Args:
        data (list): Detailed match data from openligadb.

    Returns:
        A pd.DataFrame containing match data in internal format.
    """
    matches = pd.DataFrame(map(parse_match, data))
    cols = ['homeScore', 'guestScore', 'locID']
    matches[cols] = matches[cols].astype('Int64')
    cols = ['datetime', 'datetimeUTC']
    matches[cols] = matches[cols].apply(pd.to_datetime)
    return matches


def parse_match(match: dict) -> dict:
    """Parses a single match into internal format.

    Args:
        match (dict): A single match in the format of openligadb.

    Returns:
        A dictionary representing details of a single match in internal format.
    """
    if match['matchResults']:
        score = {'home': match['matchResults'][0]['pointsTeam1'],
                 'guest': match['matchResults'][0]['pointsTeam2']}
    else:
        score = {'home': None, 'guest': None}
    if match['location']:
        loc = {'ID': match['location']['locationID'],
               'city': match['location']['locationCity'],
               'stadium': match['location']['locationStadium']}
    else:
        loc = {'ID': None, 'city': None, 'stadium': None}
    return {
        'season': match['leagueSeason'],
        'division': match['leagueShortcut'],
        'datetime': match['matchDateTime'],
        'datetimeUTC': match['matchDateTimeUTC'],
        'matchday': match['group']['groupOrderID'],
        'homeID': match['team1']['teamId'],
        'homeName': match['team1']['teamName'],
        'homeIcon': match['team1']['teamIconUrl'],
        'guestID': match['team2']['teamId'],
        'guestName': match['team2']['teamName'],
        'guestIcon': match['team2']['teamIconUrl'],
        'finished': match['matchIsFinished'],
        'homeScore': score['home'],
        'guestScore': score['guest'],
        'locID': loc['ID'],
        'locCity': loc['city'],
        'locStadium': loc['stadium']
    }


def store_season(season: int, matches: pd.DataFrame):
    """Stores a season to local cache.

    Args:
        season (int): Year of the season
        matches (pd.DataFrame): Match data in internal format
    """
    matches.reset_index(drop=True, inplace=True)
    matches.drop(matches[~matches['finished']].index, axis=0, inplace=True)
    matches.drop('finished', axis=1, inplace=True)
    matches.to_csv(f'{g_cache_path}/matches_{season}.csv', index=False)
    avail = load_cache_index()
    cols = ['cachedMatchdays', 'cached', 'cachedDatetime']
    matchdays = matches['matchday'].max()
    timestamp = str(datetime.now())
    avail.loc[avail['season'] == season, cols] = [matchdays, True, timestamp]
    store_cache_index(avail)


def fetch_avail_seasons():
    """Fetches and caches all seasons available on openligadb.
    """
    responses = asyncio.run(fetch_queries([{'action': 'getavailableleagues'}]))
    leagues = [{'IDs': resp['leagueId'], 'season': int(resp['leagueSeason']),
                'division': resp['leagueShortcut']}
               for resp in responses[0]['response']
               if (resp['leagueShortcut'] in g_divisions)]
    leagues = filter(lambda l: l['season'] >= g_season_lower_limit, leagues)
    avail = pd.DataFrame(leagues).sort_values(['season', 'division'])
    avail = avail.groupby('season').agg(list).reset_index()
    cols = ['availMatchdays', 'cached', 'cachedMatchdays', 'cachedDatetime']
    avail[cols] = [None, False, 0, None]
    cache = load_cache_index(False)
    if not cache.empty:
        avail = pd.concat([avail[~avail.season.isin(cache.season)], cache])
    store_cache_index(avail)


def fetch_avail_matchdays():
    """Fetches and caches number of available match days for each season.
    """
    avail = load_cache_index()
    leagues = avail.explode('division')
    leagues = leagues[['division', 'season']]
    leagues.insert(0, 'action', 'getavailablegroups')
    queries = leagues.to_dict('records')
    responses = asyncio.run(fetch_queries(queries))
    responses = map(lambda x: x['response']['groupOrderID'], responses)
    data = [
        {'season': r['params']['season'], 'availMatchdays': max(r['response'])}
        for r in responses]
    df = pd.DataFrame(data).groupby('season').agg(max)
    df['availMatchdays'] = df['availMatchdays'].astype('Int64')
    avail.set_index('season', inplace=True)
    avail.update(df)
    store_cache_index(avail)


def fetch_next_matches():
    """Fetches and caches next match(es) which have not taken place yet.
    If there are simultaneous matches, multiple matches will be cached.
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
    """Gathers multiple queries and sends requests asynchronously. See query().

    Args:
        queries (list): List of queries.

    Returns:
        A List of responses.
    """
    async with aiohttp.ClientSession() as session:
        tasks = map(
            lambda params: asyncio.ensure_future(query(session, params)),
            queries)
        responses = await asyncio.gather(*tasks)
        return responses


async def query(session: aiohttp.client.ClientSession, params: dict) -> dict:
    """Constructs a request and parses response.

    Args:
        session: aiohttp client session for asynchronous requests.
        params (dict): A dictionary containg request parameters in the
                       order required.

    Returns:
        A dictionary containing the request parameters and the corresponding
        response.
    """
    paramStr = '/'.join(map(str, params.values()))
    url = f'https://api.openligadb.de/{paramStr}'
    async with session.get(url) as resp:
        # print(f'Fetching {url}')
        response = await resp.json()
        return {'params': params, 'response': response}


def load_cache_index(fetchIfEmpty: bool = True) -> pd.DataFrame:
    """Reads cache index and returns its content as pd.DataFrame.

    Args:
        fetchIfEmpty (bool): Determines if available seasons should be fetched
                             if the local cache is empty.

    Returns:
        A pd.DataFrame representing the content of the cache index (might be
        an empty pd.DataFrame).
    """
    path = f'{g_cache_path}/index.csv'
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=['cachedDatetime'])
        df['availMatchdays'] = df['availMatchdays'].astype('Int64')
        df['division'] = df['division'].apply(literal_eval)
    elif fetchIfEmpty:
        fetch_avail_seasons()
        df = load_cache_index(False)
    else:
        df = pd.DataFrame()
    return df


def store_cache_index(data: pd.DataFrame):
    """Stores given pd.DataFrame as cache index.

    Args:
        data (pd.DataFrame): A pd.DataFrame representing the cache index.
    """
    data.to_csv(f'{g_cache_path}/index.csv', index=False)
