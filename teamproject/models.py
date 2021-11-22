"""
This module contains code for a prediction models.
"""

from collections import Counter
import json
import pandas as pd
import numpy as np

"""
This module contains code for prediction models.
"""


from collections import Counter
import json

class BaselineAlgo:
    """
    A model that predicts the winner based on the outcome of past games between
    the 2 teams
    """

    def __init__(self, matches):
        self.matches = matches
        self.df = pd.DataFrame(self.matches)
        

    def predict_winner(self, home_team: str, guest_team: str):
        df = self.df

        # get matches between the two given teams
        team1 = df.homeClub.values
        team2 = df.guestClub.values

        matches = df[((team1 == home_team) & (team2 == guest_team)) |
                     ((team1 == guest_team) & (team2 == home_team))]

        # if no matches exist: return average home winrate, average guest winrate and draw probability
        if len(matches) == 0:
            home_score = df.homeScore.values
            guest_score = df.guestScore.values

            wins_home_team_total = np.sum(home_score > guest_score)
            wins_guest_team_total = np.sum(home_score < guest_score)
            draws_total = np.sum(home_score == guest_score)

            # returns probability for each of the 3 events in a list
            return [wins_home_team_total / len(df), draws_total / len(df), wins_guest_team_total / len(df)]

        # if matches exist: collect results in matches between them
        home_club = matches.homeClub.values
        guest_club = matches.guestClub.values

        home_score = matches.homeScore.values
        guest_score = matches.guestScore.values

        wins_home_team = np.sum((home_score > guest_score) & (home_club == home_team) |
                                (home_score < guest_score) & (guest_club == home_team))

        wins_guest_team = np.sum((home_score > guest_score) & (home_club == guest_team) |
                                 (home_score < guest_score) & (guest_club == guest_team))

        draws = np.sum(matches['homeScore'] == matches['guestScore'])

        # returns probability for each of the 3 events in a list
        return [wins_home_team / len(matches), draws / len(matches), wins_guest_team / len(matches)]


