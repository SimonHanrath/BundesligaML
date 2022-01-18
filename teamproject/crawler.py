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


def get_data(fromSeason: int, fromMatchday: int, toSeason: int,
             toMatchday: int, forceUpdate: bool = False) -> pd.DataFrame:
    """Returns match data within a given interval.

    Args:
        fromSeason (int): Season of lower interval limit.
        fromMatchday (int): Day of lower interval limit.
        toSeason (int): Season of upper interval limit.
        toMatchday (int): Day of upper interval limit.
        forceUpdate (bool): Force re-caching of seasons in interval. Defaults
                            to False.

    Returns:
        Match data as pd.DataFrame (can be empty)
    """
    fetchIfEmpty = True
    avail = load_cache_index(fetchIfEmpty)
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
        store_matchdata(str(key), pd.concat(frames))
    # assemble interval from cache
    if seasonList:
        frames = [load_matchdata(str(season)) for season in seasonList]
        data = pd.concat(frames, ignore_index=True)
        lt = (data['season'] == fromSeason) & (data['matchday'] < fromMatchday)
        gt = (data['season'] == toSeason) & (data['matchday'] > toMatchday)
        data.drop(data[lt | gt].index, axis=0, inplace=True)
        data.reset_index(drop=True, inplace=True)
    else:
        data = pd.DataFrame()
    return data


def get_teams(data: pd.DataFrame) -> pd.DataFrame:
    """Computes all teams from given match data.

    Args:
        data (pd.DataFrame): Match data of any time interval.

    Returns:
        A pd.DataFrame representing teams including team details.
    """
    homeTeams = data[['homeTeamID', 'homeTeamName', 'homeTeamIcon']]
    guestTeams = data[['guestTeamID', 'guestTeamName', 'guestTeamIcon']]
    cols = ['ID', 'name', 'icon']
    homeTeams.set_axis(cols, axis=1, inplace=True)
    guestTeams.set_axis(cols, axis=1, inplace=True)
    teams = pd.concat([homeTeams, guestTeams], ignore_index=True)
    teams = teams.drop_duplicates().sort_values('name')
    teams.reset_index(drop=True, inplace=True)
    return teams


def refresh_ui_cache():
    """Collects and executes all functions refreshing cached data which will be
    displayed in the GUI. It is possible to call the functions separately to
    decrease startup time of the GUI.
    """
    fetch_avail_seasons()
    fetch_avail_matchdays()
    fetch_next_matches()


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
    cache = load_cache_index()
    if not cache.empty:
        avail = pd.concat([avail[~avail.season.isin(cache.season)], cache])
    store_cache_index(avail)


def fetch_avail_matchdays():
    """Fetches and caches number of available match days for each season.
    """
    fetchIfEmpty = True
    avail = load_cache_index(fetchIfEmpty)
    leagues = avail.explode('division')
    leagues = leagues[['division', 'season']]
    leagues.insert(0, 'action', 'getavailablegroups')
    queries = leagues.to_dict('records')
    responses = asyncio.run(fetch_queries(queries))
    print(responses)
    matchdays = [{
        'season': res['params']['season'],
        'availMatchdays':
        max(res['response'], key=lambda x: x['groupOrderID'])['groupOrderID']}
        for res in responses]
    data = pd.DataFrame(matchdays).groupby('season').agg(max)
    data['availMatchdays'] = data['availMatchdays'].astype('Int64')
    avail.set_index('season', inplace=True)
    avail.update(data)
    avail.reset_index(inplace=True)
    store_cache_index(avail)


def fetch_next_matches():
    """Fetches and caches next match(es) which have not taken place yet.
    If there are simultaneous matches, multiple matches will be cached.
    """
    fetchIfEmpty = True
    avail = load_cache_index(fetchIfEmpty)
    current = avail.explode('division')
    current = current[['division', 'season']]
    currentSeason = current['season'].max()
    current = current[current['season'] == currentSeason]
    current.insert(0, 'action', 'getmatchdata')
    queries = current.to_dict('records')
    responses = asyncio.run(fetch_queries(queries))
    data = pd.concat(map(lambda d: parse_league(d['response']), responses))
    store_matchdata(str(currentSeason), data.copy())
    data = data[data['datetimeUTC'] >= pd.Timestamp.utcnow()]
    data = data[data['datetimeUTC'] == data['datetimeUTC'].min()] # TO-DO: letzte/nächste Spieltage (nicht Uhrzeit)
    data['finished'] = True
    store_matchdata('next', data)


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
    score = list(filter(lambda d: d['resultName'] == 'Endergebnis',
                        match['matchResults']))
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
        'homeTeamID': match['team1']['teamId'],
        'homeTeamName': match['team1']['teamName'],
        'homeTeamIcon': match['team1']['teamIconUrl'],
        'guestTeamID': match['team2']['teamId'],
        'guestTeamName': match['team2']['teamName'],
        'guestTeamIcon': match['team2']['teamIconUrl'],
        'finished': match['matchIsFinished'],
        'homeScore': score[0]['pointsTeam1'] if score else None,
        'guestScore': score[0]['pointsTeam2'] if score else None,
        'locID': loc['ID'],
        'locCity': loc['city'],
        'locStadium': loc['stadium']
    }


def load_cache_index(fetchIfEmpty: bool = False) -> pd.DataFrame:
    """Reads cache index and returns its content as pd.DataFrame.

    Args:
        fetchIfEmpty (bool): Determines if available seasons should be fetched
                             if the local cache is empty. Defaults to False.

    Returns:
        A pd.DataFrame representing the content of the cache index (might be
        an empty pd.DataFrame).
    """
    path = f'{g_cache_path}/index.csv'
    if os.path.exists(path):
        data = pd.read_csv(path, parse_dates=['cachedDatetime'])
        data['availMatchdays'] = data['availMatchdays'].astype('Int64')
        data['division'] = data['division'].apply(literal_eval)
    elif fetchIfEmpty:
        fetch_avail_seasons()
        data = load_cache_index()
    else:
        data = pd.DataFrame()
    return data


def load_matchdata(suffix: str) -> pd.DataFrame:
    """Reads matches from cache and returns its content as pd.DataFrame.

    Args:
        suffix (str): File suffix (identifier) of the matchdata.

    Returns:
        A pd.DataFrame representing match data in internal format.
    """
    path = f'{g_cache_path}/matchdata_{suffix}.csv'
    if os.path.exists(path):
        matches = pd.read_csv(path, parse_dates=['datetime', 'datetimeUTC'])
        matches['locID'] = matches['locID'].astype('Int64')
    else:
        matches = pd.DataFrame()
        print(f'File not found: {path}')
    return matches


def store_cache_index(data: pd.DataFrame):
    """Stores given pd.DataFrame as cache index in CSV file format.

    Args:
        data (pd.DataFrame): A pd.DataFrame representing the cache index.
    """
    if not os.path.exists(g_cache_path):
        os.mkdir(g_cache_path)
    data.to_csv(f'{g_cache_path}/index.csv', index=False)


def store_matchdata(suffix: str, data: pd.DataFrame):
    """Stores match data to local cache in CSV file format.

    Args:
        suffix (str): File suffix (identifier) of given match data.
        data (pd.DataFrame): Match data in internal format.
    """
    if not os.path.exists(g_cache_path):
        os.mkdir(g_cache_path)
    data.reset_index(drop=True, inplace=True)
    data.drop(data[~data['finished']].index, axis=0, inplace=True)
    data.drop('finished', axis=1, inplace=True)
    data.to_csv(f'{g_cache_path}/matchdata_{suffix}.csv', index=False)
    if suffix != 'next':
        fetchIfEmpty = True
        avail = load_cache_index(fetchIfEmpty)
        season = int(suffix)
        cols = ['availMatchdays', 'cachedMatchdays', 'cached',
                'cachedDatetime']
        days = data['matchday'].max()
        now = str(datetime.now())
        avail.loc[avail['season'] == season, cols] = [days, days, True, now]
        store_cache_index(avail)
