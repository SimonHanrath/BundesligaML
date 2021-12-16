# Use this file to test your crawler.
from teamproject import crawler
import pandas as pd


def test_get_data():
    lowerLimitYear = 2020
    upperLimitYear = 2020
    data = crawler.get_data(lowerLimitYear, 1, upperLimitYear, 38)
    # check dtypes
    assert data.date.dtype == "datetime64[ns]"
    assert data.homeClubId.dtype == "int64"
    assert data.guestClubId.dtype == "int64"
    assert data.homeClub.dtype == "object"
    assert data.guestClub.dtype == "object"
    assert data.homeScore.dtype == "int64"
    assert data.guestScore.dtype == "int64"
    # check data format
    assert (data.homeClub != "").all()
    assert (data.guestClub != "").all()
    assert (data.homeScore >= 0).all()
    assert (data.guestScore >= 0).all()
    assert (data.homeClub != data.guestClub).all()
    assert (data.homeClubId != data.guestClubId).all()
    # check interval
    assert (data.date >= pd.Timestamp(lowerLimitYear, 1, 1)).all()
    assert (data.date <= pd.Timestamp(upperLimitYear+1, 12, 31)).all()
