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
    >>> model.predict("Team1", "Team2")
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

    def predict(self, homeTeam: str, guestTeam: str)->list:
        """Predicts the winner between homeTeam and guestTeam based on 
           past matches between them

        Args:
            homeTeam (str): Name of the home team 
            guestTeam (str): Name of the guest team

        Returns:
            A list containig the probabilties for the homeTeam winning, a draw 
            and the guestTeam winning in that order
        """
        df = self.df

        # get matches between the two given teams
        team1 = df.homeClub.values
        team2 = df.guestClub.values

        matches = df[((team1 == homeTeam) & (team2 == guestTeam)) |
                     ((team1 == guestTeam) & (team2 == homeTeam))]

        # if no matches exist: return average home winrate, average guest winrate and draw probability
        if len(matches) == 0:
            homeScore = df.homeScore.values
            guestScore = df.guestScore.values

            winsHomeTeamTotal = np.sum(homeScore > guestScore)
            winsGuestTeamTotal = np.sum(homeScore < guestScore)
            drawsTotal = np.sum(homeScore == guestScore)

            # returns probability for each of the 3 events in a list
            return [winsHomeTeamTotal / len(df), drawsTotal / len(df), winsGuestTeamTotal / len(df)]

        # if matches exist: collect results in matches between them
        homeClub = matches.homeClub.values
        guestClub = matches.guestClub.values

        homeScore = matches.homeScore.values
        guestScore = matches.guestScore.values

        winsHomeTeam = np.sum((homeScore > guestScore) & (homeClub == homeTeam) |
                                (homeScore < guestScore) & (guestClub == homeTeam))

        winsGuestTeam = np.sum((homeScore > guestScore) & (homeClub == guestTeam) |
                                 (homeScore < guestScore) & (guestClub == guestTeam))

        draws = np.sum(matches['homeScore'] == matches['guestScore'])

        # returns probability for each of the 3 events in a list
        return [winsHomeTeam / len(matches), draws / len(matches), winsGuestTeam / len(matches)]




class PoissonRegression:
    """A model that predicts the winner based on fitting a poisson distribution
       for both playing teams to estimate the probabilty for each possible outcome
       score.

    To use:
    >> model = PoissonRegression(df)
    >> model.predict("Team1", "Team2")
    [0.6, 0.2, 0.2]

    Attributes:
        goalModelData: A pandas dataframe containig the matches to consider for predictions
        poissonModel: The model for predicting the probability for x goals in a mach
        between the team and an opponent
    """

    def __init__(self, df):
        """Inits PoissonRegression with the given Dataframe

        Args:
            df: A pandas Dataframe containig the matches to consider for predictions
        """
        self.df = df

        self.teams = np.unique(self.df['guestClub'])

        self.goalModelData = pd.concat([df[['homeClub', 'guestClub', 'homeScore']].assign(home=1).rename(
            columns={'homeClub': 'team', 'guestClub': 'opponent', 'homeScore': 'goals'}),
            df[['guestClub', 'homeClub', 'guestScore']].assign(home=0).rename(
                columns={'guestClub': 'team', 'homeClub': 'opponent', 'guestScore': 'goals'})])

        self.poissonModel = smf.glm(formula="goals ~ home + team + opponent", data=self.goalModelData,
                                    family=sm.families.Poisson()).fit()

    def predict(self, homeTeam: str, guestTeam: str, maxGoals=10) -> list:
        """Predicts the winner between homeTeam and guestTeam based on 
           the poisson distributions over their expected goal amount

        Args:
            homeTeam (str): Name of the home team 
            guestTeam (str): Name of the guest team
            maxGoals (int): max amount of goals per team to consider

        Returns:
            A list containig the probabilties for the homeTeam winning, a draw 
            and the guestTeam winning in that order
        """
        model = self.poissonModel

        if homeTeam in self.teams and guestTeam in self.teams:
            homeGoalsAvg = model.predict(pd.DataFrame(data={'team': homeTeam,
                                                            'opponent': guestTeam, 'home': 1},
                                                      index=[1])).values[0]
            awayGoalsAvg = model.predict(pd.DataFrame(data={'team': guestTeam,
                                                            'opponent': homeTeam, 'home': 0},
                                                      index=[1])).values[0]
        else:
        	# if one team is unknown, assume avg home and away goals
            homeGoalsAvg = sum(self.df['homeScore']) / len(self.df['homeScore'])
            awayGoalsAvg = sum(self.df['guestScore']) / len(self.df['guestScore'])

        teamPred = [[poisson.pmf(i, teamAvg) for i in range(0, maxGoals + 1)] for teamAvg in
                    [homeGoalsAvg, awayGoalsAvg]]
        resultMatrix = np.outer(np.array(teamPred[0]), np.array(teamPred[1]))

        homeTeamWin = np.sum(np.tril(resultMatrix, -1))
        guestTeamWin = np.sum(np.triu(resultMatrix, 1))
        draw = np.sum(np.diag(resultMatrix))

        return [homeTeamWin, draw, guestTeamWin]





