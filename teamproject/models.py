"""
This module contains code for prediction models.
"""

from scipy.stats import poisson,skellam
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf



class BaselineAlgo:
    """A model that predicts the winner based on the outcome of past games between
       the 2 teams.

    To use:
    >>> model = BaselineAlgo(df)
    >>> model.predict_winner("Team1", "Team2")
    [0.6, 0.2, 0.2]

    Attributes:
        df: A pandas Dataframe containig the matches to consider for predictions
    """

    def __init__(self, df):
        """Inits BaselineAlgo with the given Dataframe

        Args:
            df: A pandas Dataframe containig the matches to consider for predictions
        """
        self.df = df

    def predict_winner(self, home_team: str, guest_team: str)->list:
        """Predicts the winner between home_team and guest_team based on 
           past matches between them

        Args:
            home_team (str): Name of the home team 
            guest_team (str): Name of the guest team

        Returns:
            A list containig the probabilties for the home_team winning, a draw 
            and the guest_team winning in that order
        """
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




class PoissonRegression:
    """A model that predicts the winner based on fitting a poisson distribution
       for both playing teams to estimate the probabilty for each possible outcome
       score.

    To use:
    >>> model = PoissonRegression(df)
    >>> model.predict_winner("Team1", "Team2")
    [0.6, 0.2, 0.2]

    Attributes:
        goal_model_data: A pandas dataframe containig the matches to consider for predictions
        poisson_model: The model for predicting the probability for x goals in a mach
        between the team and an opponent
    """

    def __init__(self, df):
        """Inits PoissonRegression with the given Dataframe

        Args:
            df: A pandas Dataframe containig the matches to consider for predictions
        """
        self.goal_model_data = pd.concat([df[['homeClub','guestClub','homeScore']].assign(home=1).rename(
            columns={'homeClub':'team', 'guestClub':'opponent','homeScore':'goals'}),
           df[['guestClub','homeClub','guestScore']].assign(home=0).rename(
            columns={'guestClub':'team', 'homeClub':'opponent','guestScore':'goals'})])

        self.poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=self.goal_model_data, 
                        family=sm.families.Poisson()).fit()

    
    def predict_winner(self, home_team:str, guest_team:str, max_goals=10)->list:
        """Predicts the winner between home_team and guest_team based on 
           the poisson distributions over their expected goal amount

        Args:
            home_team (str): Name of the home team 
            guest_team (str): Name of the guest team
            max_goals (int): max amount of goals per team to consider

        Returns:
            A list containig the probabilties for the home_team winning, a draw 
            and the guest_team winning in that order
        """
        goal_model_data = self.goal_model_data
        model = self.poisson_model

        home_goals_avg = model.predict(pd.DataFrame(data={'team': home_team, 
                                                            'opponent': guest_team,'home':1},
                                                          index=[1])).values[0]

        away_goals_avg = model.predict(pd.DataFrame(data={'team': guest_team, 
                                                            'opponent': home_team,'home':0},
                                                          index=[1])).values[0]

        team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in [home_goals_avg, away_goals_avg]]
        result_matrix = np.outer(np.array(team_pred[0]), np.array(team_pred[1]))

        home_team_win = np.sum(np.tril(result_matrix, -1))
        guest_team_win = np.sum(np.triu(result_matrix, 1))
        draw = np.sum(np.diag(result_matrix))

        return [home_team_win, draw, guest_team_win]





