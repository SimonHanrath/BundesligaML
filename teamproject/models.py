"""
This module contains code for prediction models.
"""
from scipy.stats import poisson
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.optimize import minimize


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

    def predict(self, homeTeam: str, guestTeam: str) -> list:
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
        team1 = df.homeTeamName.values
        team2 = df.guestTeamName.values

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
        homeClub = matches.homeTeamName.values
        guestClub = matches.guestTeamName.values

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
        self.teams = np.unique(self.df['guestTeamName'])

        self.goalModelData = pd.concat([df[['homeTeamName', 'guestTeamName', 'homeScore']].assign(home=1).rename(
            columns={'homeTeamName': 'team', 'guestTeamName': 'opponent', 'homeScore': 'goals'}),
            df[['guestTeamName', 'homeTeamName', 'guestScore']].assign(home=0).rename(
                columns={'guestTeamName': 'team', 'homeTeamName': 'opponent', 'guestScore': 'goals'})])

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
        print([homeTeamWin, draw, guestTeamWin])
        return [homeTeamWin, draw, guestTeamWin]










class DixonColes:
    """Basicly Poisson Regression but with fixing for misscalculating the draw propbability
       and weighing games closer to present higher.
    To use:
    >>> model = DixonColes(df)
    >>> model.predict_winner("Team1", "Team2")
    [0.6, 0.2, 0.2]

    Attributes:
    df: A pandas Dataframe containig the matches to consider for predictions and their dates

    """

    def __init__(self, df, xi=0.0018):
        """Inits DixonColes with the given Dataframe
        Args:
            df: A pandas Dataframe containig the matches to consider for predictions
        """
        self.xi = xi
        # TODO: how to set xi?
        self.df = df
        self.teams = np.unique(self.df['guestTeamName'])

        # add column containing the time difference to the newest game
        maxTime = max(pd.to_datetime(self.df.date.values))
        self.df['time_dif'] = (maxTime - pd.to_datetime(self.df.date.values)).days

        self.params = self.solve_parameters(self.df, self.xi)

    def rho_correction(self, x, y, lambda_x, mu_y, rho):
        """function to reweigh the probability for the low score outcome games
        Args:
            x (array of int): #goals homeTeam
            y (array of int): #goals guestTeam
            lambda_x (float): term from calculating the nomal PR model
            mu_y (float): term from calculating the nomal PR model
            rho (float): term to determine magnitude of correction
        Returns:
            an array of floats representing the factors with which to multipiply the old propability
            in the PR model
        """
        return np.select(
            [
                (x == 0) & (y == 0),
                (x == 0) & (y == 1),
                (x == 1) & (y == 0),
                (x == 1) & (y == 1),
                True

            ],
            [
                1 - lambda_x * mu_y * rho,
                1 + lambda_x * rho,
                1 + (mu_y * rho),
                1 - rho,
                1
            ])

    def dc_log_like_decay(self, x, y, alpha_x, beta_x, alpha_y, beta_y, rho, gamma, t, xi):
        """helper function for fitting the Poisson distrubituion manually
        Args:
            x (int): #goals homeTeam
            y (int): #goals guestTeam
            alpha_x, beta_x, alpha_y, beta_y, (float): terms from calculating the nomal PR model
            rho, gamma (float) : values from the minimize function
            t (array of int): days between latest timestamp in data and current
            xi : factor for the timedecay in the weighing
        Returns:
            an array of floats representing the log likelihoods of observing the score under the
            distribution described by the given parameters
        """
        lambda_x, mu_y = np.exp(alpha_x + beta_y + gamma), np.exp(alpha_y + beta_x)
        return np.exp(-xi*t) * (np.log(self.rho_correction(x, y, lambda_x, mu_y, rho)) +
                                np.log(poisson.pmf(x, lambda_x)) + np.log(poisson.pmf(y, mu_y)))

    def estimate_paramters(self, params, teams, dataset, nTeams, homeGoals, awayGoals, xi):
        """function to estimate how good the current parameters describe the df
        Args:
            params (dict): contains attack and defend values for each team as well as rho and gamma
            teams (list of string): name of teams
            dataset (pd.dataFrame): the current df
            n_teams : #teams
            home_goals, away_goals (int): #goals for both teams
            xi : factor for the timedecay in the weighing
        Returns:
        """
        scoreCoefs = dict(zip(teams, params[:nTeams]))
        defendCoefs = dict(zip(teams, params[nTeams:(2 * nTeams)]))

        scoreCoefsHomeTeam = np.array([scoreCoefs[team] for team in dataset.homeTeamName.values])
        defendCoefsHomeTeam = np.array([defendCoefs[team] for team in dataset.homeTeamName.values])
        scoreCoefsAwayTeam = np.array([scoreCoefs[team] for team in dataset.guestTeamName.values])
        defendCoefsAwayTeam = np.array([defendCoefs[team] for team in dataset.guestTeamName.values])

        rho, gamma = params[-2:]
        rho = np.repeat(rho, len(homeGoals))
        gamma = np.repeat(gamma, len(homeGoals))

        timeDifs = dataset.time_dif.values

        logLike = self.dc_log_like_decay(homeGoals, awayGoals, scoreCoefsHomeTeam, defendCoefsHomeTeam,
                                         scoreCoefsAwayTeam, defendCoefsAwayTeam, rho, gamma, timeDifs, xi)

        return -sum(logLike)

    def solve_parameters(self, dataset, xi, initVals=None, options={'disp': True, 'maxiter': 100},
                         constraints=[{'type': 'eq', 'fun': lambda x: sum(x[:20])-20}], **kwargs):
        """tries to approximate the best parameters to fit the function
           basicly like PR but with the two fixes
        Args:
            init_vals (dict): contains attack and defend values for each team as well as rho and gamma
            options (dict): contains max interations the minize algo should perform and whether info should be printed
            dataset (pd.dataFrame): the current df
            constraints (dict): contrains for running the minimize
            **kwargs (): no clue what this is lol
        Returns:
            a dictionary with the best estimate for the paramters
        """
        teams = np.sort(dataset['homeTeamName'].unique())
        # check for no weirdness in dataset
        awayTeams = np.sort(dataset['guestTeamName'].unique())
        if not np.array_equal(teams, awayTeams):
            raise ValueError("Something's not right")

        nTeams = len(teams)

        if initVals is None:
            # random initialisation of model parameters
            # standart_params = self.standart_params

            initVals = np.concatenate((np.random.uniform(0, 1, (nTeams)),  # attack strength
                                       np.random.uniform(0, -1, (nTeams)),  # defence strength
                                       np.array([0, 1.0])  # rho (score correction), gamma (home advantage)
                                       ))
        x = dataset.homeScore.values
        y = dataset.guestScore.values
        opt_output = minimize(lambda p: self.estimate_paramters(p, teams, dataset, nTeams, x, y, xi), initVals, options=options, constraints=constraints, **kwargs)

        return dict(zip(["attack_" + team for team in teams] +
                        ["defence_" + team for team in teams] +
                        ['rho', 'home_adv'],
                        opt_output.x))

    def predict(self, homeClub: str, guestClub: str, maxGoals=10):
        """Predicts the winner between homeTeam and guestTeam based on
           the poisson distributions over their expected goal amount
        Args:
            homeClub (str): Name of the home team
            guestClub (str): Name of the guest team
            maxGoals (int): max amount of goals per team to consider
        Returns:
            A list containig the probabilties for the homeTeam winning, a draw
            and the guestTeam winning in that order
        """
        paramsDict = self.params

        if homeClub in self.teams and guestClub in self.teams:
            teamAvgs = [
                np.exp(paramsDict['attack_' + homeClub] + paramsDict['defence_' + guestClub] + paramsDict['home_adv']),
                np.exp(paramsDict['defence_' + homeClub] + paramsDict['attack_' + guestClub])]

        else:
            teamAvgs = [sum(self.df['homeScore']) / len(self.df['homeScore']),
                        sum(self.df['guestScore']) / len(self.df['guestScore'])]

        teamPred = [[poisson.pmf(i, teamAvg) for i in range(0, maxGoals + 1)] for teamAvg in teamAvgs]

        outputMatrix = np.outer(np.array(teamPred[0]), np.array(teamPred[1]))

        correctionMatrix = np.array([[self.rho_correction(
            homeGoals, awayGoals, teamAvgs[0], teamAvgs[1], paramsDict['rho'])
            for awayGoals in range(2)] for homeGoals in range(2)])
        outputMatrix[:2, :2] = outputMatrix[:2, :2] * correctionMatrix

        homeTeamWin = np.sum(np.tril(outputMatrix, -1))
        guestTeamWin = np.sum(np.triu(outputMatrix, 1))
        draw = np.sum(np.diag(outputMatrix))
        return [homeTeamWin, draw, guestTeamWin]
