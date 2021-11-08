"""
This module contains code for a prediction models.
"""

from collections import Counter
import json


class ExperienceAlwaysWins:

    """
    An example model that predicts the winner
    solely based on number of games played.
    """

    def __init__(self, matches):
        # We just count the number of games played by all teams and ignore
        # the winner:
        self.num_games = (
            Counter(matches.home_team) +
            Counter(matches.guest_team))

    def predict_winner(self, home_team, guest_team):
        """Cast prediction based on the "learned" parameters."""
        if self.num_games[home_team] >= self.num_games[guest_team]:
            return home_team
        else:
            return guest_team


"""
This module contains code for prediction models.
"""


from collections import Counter
import json


class ExperienceAlwaysWins:
    """
    An example model that predicts the winner predicts the winner
    solely based on number of games played.
    """

    def __init__(self, matches):
        # We just count the number of games played by all teams and ignore
        # the winner:
        print(matches)
        self.num_games = (
                Counter(matches.home_team) +
                Counter(matches.guest_team))
        print(self.num_games)

    def predict_winner(self, home_team, guest_team):
        """Cast prediction based on the "learned" parameters."""
        if self.num_games[home_team] >= self.num_games[guest_team]:
            return home_team
        else:
            return guest_team


class BaselineAlgo:
    """
    An example model that predicts the winner based on past games between
    the 2 teams
    """

    def __init__(self, matches):
        self.matches = matches

    def predict_winner(self, home_team:str, guest_team:str):
        wins_home_team = 0
        wins_guest_team = 0
        draws = 0
        num_matches = 0
        draws_total = 0

        for match in self.matches:
            # count draws
            if match["homeScore"] == match["guestScore"]:
                draws_total += 1

            # use sets to easily detect when right teams play
            playing_clubs = set([match['homeClub'], match['guestClub']])
            # if the right teams play measure the result
            if playing_clubs == set([home_team, guest_team]):
                num_matches += 1
                if match["homeScore"] > match["guestScore"]:
                    if match["homeClub"] == home_team:
                        wins_home_team += 1
                    else:
                        wins_guest_team += 1
                elif match["homeScore"] < match["guestScore"]:
                    if match["homeClub"] == home_team:
                        wins_guest_team += 1
                    else:
                        wins_home_team += 1
                else:
                    draws += 1
        # in case no data is available, calculate average draw probability
        # could do same for home vs visiting but I am not sure whether this
        # is needed
        if num_matches == 0:
            print("No matches of the two teams found")
            draws_total = draws_total/len(self.matches)
            return [(1-draws_total)/2, draws_total, (1-draws_total)/2]

        # return win probability (currently just a list but can easily be changed)
        return [wins_home_team/num_matches, draws/num_matches, wins_guest_team/num_matches]

