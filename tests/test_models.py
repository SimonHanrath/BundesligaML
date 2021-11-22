# Use this file to test your prediction algorithms.

from teamproject import models
import pandas as pd

# It is important to test your algorithms against handcrafted data to reliably
# cover edge cases! So feel free to make up several test datasets in the same
# format as would be returned by your crawler:
test_dataset = [
{"date": "2018-08-24T18:30:00Z", "homeClub": "A", "guestClub": "B", "homeScore": 3, "guestScore": 1},
{"date": "2018-08-24T18:30:00Z", "homeClub": "A", "guestClub": "B", "homeScore": 1, "guestScore": 2},
{"date": "2018-08-24T18:30:00Z", "homeClub": "B", "guestClub": "A", "homeScore": 3, "guestScore": 1},
{"date": "2018-08-24T18:30:00Z", "homeClub": "A", "guestClub": "B", "homeScore": 1, "guestScore": 1},
{"date": "2018-08-24T18:30:00Z", "homeClub": "C", "guestClub": "B", "homeScore": 2, "guestScore": 1}]


def test_BaselineAlgo():
    model = models.BaselineAlgo(test_dataset)
    winner = model.predict_winner

    # 4 matches between A and B of which B wins two and one ends in a draw
    assert sum(winner('A', 'B')) == sum(winner('B', 'A')) == 1
    assert winner('A', 'B') == [0.25,0.25,0.5]
    assert winner('B', 'A') == [0.5,0.25,0.25]

    # 1 match between B,C which  C  wins
    assert sum(winner('C', 'B')) == sum(winner('B', 'C')) == 1
    assert winner('B', 'C') == [0,0,1]
    assert winner('C', 'B') == [1,0,0]

    # No matches between A,C therefore return avg. probability
    assert sum(winner('A', 'C')) == sum(winner('C', 'A')) == 1
    assert winner('A', 'C') == winner('C', 'A') == [0.6,0.2,0.2]
    
    # No matches between A,D herefore return avg. probability
    assert sum(winner('A', 'D')) == sum(winner('D', 'A')) == 1
    assert winner('A', 'D') == winner('D', 'A') == [0.6,0.2,0.2]






