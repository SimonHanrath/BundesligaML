import pandas as pd
from teamproject import crawler


# test fetching and caching of available data
def test_load_cache_index():
    crawler.fetch_avail_seasons()
    crawler.fetch_avail_matchdays()
    data = crawler.load_cache_index()
    # check types
    assert data['cached'].dtype == 'bool'
    assert data['division'].dtype == 'object'
    assert pd.api.types.is_integer_dtype(data['season'])
    assert pd.api.types.is_integer_dtype(data['availMatchdays'])
    assert pd.api.types.is_integer_dtype(data['cachedMatchdays'])
    assert pd.api.types.is_datetime64_any_dtype(data['cachedDatetime'])
    # check data format and correctness
    assert (data['season'] != '').all()
    assert (data['division'] != '').all()
    assert (data['availMatchdays'] > 0).all()
    assert (~data['cached'] | (data['cachedMatchdays'] > 0)).all()
    assert not data['season'].duplicated().any()


# test fetching and caching of next matches
def test_load_matchdata():
    crawler.fetch_next_matches()
    data = crawler.load_matchdata('next')
    # check types
    assert data['division'].dtype == 'object'
    assert data['homeTeamName'].dtype == 'object'
    assert data['homeTeamIcon'].dtype == 'object'
    assert data['guestTeamName'].dtype == 'object'
    assert data['guestTeamIcon'].dtype == 'object'
    assert pd.api.types.is_integer_dtype(data['season'])
    assert pd.api.types.is_integer_dtype(data['matchday'])
    assert pd.api.types.is_integer_dtype(data['homeTeamID'])
    assert pd.api.types.is_integer_dtype(data['guestTeamID'])
    assert pd.api.types.is_integer_dtype(data['locID'])
    assert pd.api.types.is_datetime64_any_dtype(data['datetime'])
    assert pd.api.types.is_datetime64_any_dtype(data['datetimeUTC'])
    # check data format and correctness
    assert (data['season'] != '').all()
    assert (data['division'] != '').all()
    assert (data['matchday'] > 0).all()
    assert (data['homeTeamName'] != '').all()
    assert (data['homeTeamIcon'] != '').all()
    assert (data['guestTeamName'] != '').all()
    assert (data['guestTeamIcon'] != '').all()
    assert (data['homeTeamID'] != data['guestTeamID']).all()
    assert (data['homeTeamName'] != data['guestTeamName']).all()
    timeLimit = pd.Timestamp.utcnow() - pd.offsets.Minute(90)
    assert (data['datetimeUTC'] >= timeLimit).all()


def test_get_data():
    fromSeason = 2020
    fromMatchday = 3
    toSeason = 2020
    toMatchday = 20
    data = crawler.get_data(fromSeason, fromMatchday, toSeason, toMatchday)
    # check types
    assert data['division'].dtype == 'object'
    assert data['homeTeamName'].dtype == 'object'
    assert data['homeTeamIcon'].dtype == 'object'
    assert data['guestTeamName'].dtype == 'object'
    assert data['guestTeamIcon'].dtype == 'object'
    assert data['locCity'].dtype == 'object'
    assert data['locStadium'].dtype == 'object'
    assert pd.api.types.is_integer_dtype(data['season'])
    assert pd.api.types.is_integer_dtype(data['matchday'])
    assert pd.api.types.is_integer_dtype(data['homeTeamID'])
    assert pd.api.types.is_integer_dtype(data['guestTeamID'])
    assert pd.api.types.is_integer_dtype(data['homeScore'])
    assert pd.api.types.is_integer_dtype(data['guestScore'])
    assert pd.api.types.is_integer_dtype(data['locID'])
    assert pd.api.types.is_datetime64_any_dtype(data['datetime'])
    assert pd.api.types.is_datetime64_any_dtype(data['datetimeUTC'])
    # check data format and correctness
    assert (data['season'] != '').all()
    assert (data['division'] != '').all()
    assert (data['matchday'] > 0).all()
    assert (data['homeTeamName'] != '').all()
    assert (data['homeTeamIcon'] != '').all()
    assert (data['guestTeamName'] != '').all()
    assert (data['guestTeamIcon'] != '').all()
    assert (data['homeScore'] >= 0).all()
    assert (data['guestScore'] >= 0).all()
    assert (data['homeTeamID'] != data['guestTeamID']).all()
    assert (data['homeTeamName'] != data['guestTeamName']).all()
    assert (data['datetimeUTC'] < pd.Timestamp.utcnow()).all()
    lower = (data['season'] > fromSeason) | (data['matchday'] >= fromMatchday)
    upper = (data['season'] < toSeason) | (data['matchday'] <= toMatchday)
    assert (lower & upper).all()


def test_get_teams():
    matchdata = crawler.get_data(2020, 1, 2020, 38)
    teams = crawler.get_teams(matchdata)
    assert teams['name'].dtype == 'object'
    assert teams['icon'].dtype == 'object'
    assert pd.api.types.is_integer_dtype(teams['ID'])
    assert (teams['name'] != '').all()
    assert (teams['icon'] != '').all()
    assert not teams.duplicated().any()
