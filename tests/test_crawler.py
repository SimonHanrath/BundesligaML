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
