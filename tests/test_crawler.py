from teamproject import crawler


def test_load_cache_index():
    df = crawler.load_cache_index()
    # check types
    assert df['season'].dtype == 'int64'
    assert df['division'].dtype == 'object'
    assert df['availMatchdays'].dtype == 'int64'
    assert df['cached'].dtype == 'bool'
    assert df['cachedMatchdays'].dtype == 'int64'
    assert df['cachedDatetime'].dtype == 'datetime64[ns]'
    # check data format and correctness
    assert (df['season'] != '').all()
    assert (df['division'] != '').all()
    assert (df['availMatchdays'] > 0).all()
    assert (~df['cached'] | (df['cachedMatchdays'] > 0)).all()


def test_get_data():
    fromSeason = 2020
    fromMatchday = 1
    toSeason = 2020
    toMatchday = 20
    df = crawler.get_data(fromSeason, fromMatchday, toSeason, toMatchday)
    # check types
    assert df['season'].dtype == 'int64'
    assert df['division'].dtype == 'object'
    assert df['datetime'].dtype == 'datetime64[ns]'
    assert df['datetimeUTC'].dtype == 'datetime64[ns, UTC]'
    assert df['matchday'].dtype == 'int64'
    assert df['homeID'].dtype == 'int64'
    assert df['homeName'].dtype == 'object'
    assert df['homeIcon'].dtype == 'object'
    assert df['guestID'].dtype == 'int64'
    assert df['guestName'].dtype == 'object'
    assert df['guestIcon'].dtype == 'object'
    assert df['homeScore'].dtype == 'int64'
    assert df['guestScore'].dtype == 'int64'
    assert df['locID'].dtype == 'Int64'
    assert df['locCity'].dtype == 'object'
    assert df['locStadium'].dtype == 'object'
    # check data format and correctness
    assert (df['season'] != '').all()
    assert (df['division'] != '').all()
    assert (df['matchday'] > 0).all()
    assert (df['homeName'] != '').all()
    assert (df['homeIcon'] != '').all()
    assert (df['guestName'] != '').all()
    assert (df['guestIcon'] != '').all()
    assert (df['homeScore'] >= 0).all()
    assert (df['guestScore'] >= 0).all()
    assert (df['homeID'] != df['guestID']).all()
    assert (df['homeName'] != df['guestName']).all()
    # check interval
    lowerLim = (df['season'] >= fromSeason) | (df['matchday'] >= fromMatchday)
    upperLim = (df['season'] <= toSeason) | (df['matchday'] <= toMatchday)
    assert (lowerLim).all()
    assert (upperLim).all()
