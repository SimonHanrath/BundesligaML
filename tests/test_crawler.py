# Use this file to test your crawler.
from teamproject import crawler
import pandas as pd

def test_fetch_data():
    file = crawler.fetch_data(2020,1,2020,38)
    data = pd.read_json(file)
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

"""
# Example test:
def test_fetch_data():
    data = crawler.fetch_data()
    assert isinstance(data, pd.DataFrame)
    assert data.home_score.dtype == 'int64'
    assert data.guest_score.dtype == 'int64'
    assert (data.home_score >= 0).all()
    assert (data.guest_score >= 0).all()
    assert (data.home_team != data.guest_team).all()
"""
