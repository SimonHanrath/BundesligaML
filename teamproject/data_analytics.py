from crawler import get_data
import matplotlib.pyplot as pp
import numpy as n

def main(data, homeClub, guestClub):
    # filePath = fetch_data(2009,180, 2021,140,'C:/Users/Philipp Wagner/Desktop/Python_Projekte/BundesligaML/teamproject/crawled_data/matches-2009-180-2021-140.json')
    fetchedMatches = data
    #fetchedMatches = get_data(2009, 180, 2021, 140)

    """Index(['season',
           'division',
           'datetime',
           'matchday',
           'homeTeamID',
           'homeTeamName',
           'guestTeamID',
           'guestTeamName',
           'homeScore',
           'guestScore',
           'goalMinsHome',          
           'goalMinsGuest'],
           dtype='object')
    """
    """Example:
    for match in fetchedMatches:
        print(match["homeScore"])
    """
    # testing list of teams in Bundesliga
    # teams = ["VfL Wolfsburg", "Borussia Dortmund", "1. FC Nürnberg", "Werder Bremen", "Hertha BSC", "1. FSV Mainz 05", "TSG 1899 Hoffenheim", "VfL Bochum", "SC Freiburg", "FC Bayern München", "VfB Stuttgart", "Hamburger SV",
    #          "Bayer Leverkusen", "Hannover 96", "Eintracht Frankfurt", "1. FC Köln", "Borussia Mönchengladbach", "FC Schalke 04" ]

    # List of all teams without duplicates
    allTeams = []
    duplicate = False
    for i in fetchedMatches.index:

        for team in allTeams:
            if fetchedMatches["homeTeamName"][i] == team:
                duplicate = True
                break
            else:
                duplicate = False
        if duplicate is False:
            allTeams.append(fetchedMatches["homeTeamName"][i])


    # wins by home team
    homeWins = 0
    for i in fetchedMatches.index:
        if fetchedMatches["homeScore"][i] > fetchedMatches["guestScore"][i]:
            homeWins = homeWins + 1


    # wins by guest team
    guestWins = 0
    for i in fetchedMatches.index:
        if fetchedMatches["homeScore"][i] < fetchedMatches["guestScore"][i]:
            guestWins = guestWins + 1


    # draw matches
    drawMatches = 0
    for i in fetchedMatches.index:
        if fetchedMatches["homeScore"][i] == fetchedMatches["guestScore"][i]:
            drawMatches = drawMatches + 1


    def matchResultsHome(homeClub):
        """matches of each team as homeClub
        Args:
            homeClub (str):
        Returns:
             Returns wins (int), loses (int) and draws(int) of the chosen HomeClub
        Example:
            print(matchResultsHome("1. FC Nürnberg"))
        """
        wins = 0
        loses = 0
        draws = 0
        for i in fetchedMatches.index:
            if fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["homeScore"][i] > fetchedMatches["guestScore"][i]:
                wins = wins + 1
            if fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["homeScore"][i] == fetchedMatches["guestScore"][i]:
                loses = loses + 1
            if fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["homeScore"][i] < fetchedMatches["guestScore"][i]:
                draws = draws + 1
        result = [wins, loses, draws]
        return result



    def matchResultsGuest(guestClub):
        """matches of each team as guestClub
            Args:
                guestClub (str):
            Returns:
                Returns wins (int), loses (int) and draws(int) of the chosen guestClub
            Example:
                print(matchResultsGuest("1. FC Nürnberg"))
        """
        wins = 0
        loses = 0
        draws = 0
        for i in fetchedMatches.index:
            if fetchedMatches["guestTeamName"][i] == guestClub and fetchedMatches["guestScore"][i] > fetchedMatches["homeScore"][i]:
                wins = wins + 1
            if fetchedMatches["guestTeamName"][i] == guestClub and fetchedMatches["guestScore"][i] == fetchedMatches["homeScore"][i]:
                loses = loses + 1
            if fetchedMatches["guestTeamName"][i] == guestClub and fetchedMatches["guestScore"][i] < fetchedMatches["homeScore"][i]:
                draws = draws + 1
        result = [wins, loses, draws]
        return result



    def specificMatchesHome(homeClub):
        """against which team were the most wins/loses/draws as a specific homeclub
            Args:
                homeClub (str): specific name of a homeClub
            Returns:
                 Returns most wins/loses/draws (int) and against which team (str)
            Example:
                print(specificMatches("1. FC Nürnberg"))
            """
        accWins = 0
        accWinsName = ""
        accLoses = 0
        accLosesName = ""
        accDraws = 0
        accDrawsName = ""
        wins = 0
        loses = 0
        draws = 0
        for team in allTeams:
            for i in fetchedMatches.index:
                if fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["guestTeamName"][i] == team and fetchedMatches["guestScore"][i] < fetchedMatches["homeScore"][i]:
                    wins = wins + 1
                if fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["guestTeamName"][i] == team and fetchedMatches["guestScore"][i] == fetchedMatches["homeScore"][i]:
                    draws = draws + 1
                if fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["guestTeamName"][i] == team and fetchedMatches["guestScore"][i] > fetchedMatches["homeScore"][i]:
                    loses = loses + 1
            if wins > accWins:
                accWins = wins
                accWinsName = team
            wins = 0
            if loses > accLoses:
                accLoses = loses
                accLosesName = team
            loses = 0
            if draws > accDraws:
                accDraws = draws
                accDrawsName = team
            draws = 0
        result = [accWinsName, accWins, accLosesName, accLoses, accDrawsName, accDraws]
        return result


    def specificMatchesGuest(guestClub):
        """against which team were the most wins/loses/draws as a specific guestclub
                Args:
                    guestClub (str): a specific guestClub name
                Returns:
                    Returns most wins/loses/draws (int) and against which team (str)
                Example:
                    print(specificMatches("1. FC Nürnberg"))
            """
        accWins = 0
        accWinsName = ""
        accLoses = 0
        accLosesName = ""
        accDraws = 0
        accDrawsName = ""
        wins = 0
        loses = 0
        draws = 0
        for team in allTeams:
            for i in fetchedMatches.index:
                if fetchedMatches["homeTeamName"][i] == guestClub and fetchedMatches["homeTeamName"][i] == team and fetchedMatches["homeScore"][i] < fetchedMatches["guestScore"][i]:
                    wins = wins + 1
                if fetchedMatches["homeTeamName"][i] == guestClub and fetchedMatches["homeTeamName"][i] == team and fetchedMatches["homeScore"][i] == fetchedMatches["guestScore"][i]:
                    draws = draws + 1
                if fetchedMatches["homeTeamName"][i] == guestClub and fetchedMatches["homeTeamName"][i] == team and fetchedMatches["homeScore"][i] > fetchedMatches["guestScore"][i]:
                    loses = loses + 1
            if wins > accWins:
                accWins = wins
                accWinsName = team
            wins = 0
            if loses > accLoses:
                accLoses = loses
                accLosesName = team
            loses = 0
            if draws > accDraws:
                accDraws = draws
                accDrawsName = team
            draws = 0
        result = [accWinsName, accWins, accLosesName, accLoses, accDrawsName, accDraws]
        return result




    def specificMatches(homeClub, guestClub):
        """shows results of the matches in the past of the homeClub against the guestClub
                Args:
                    guestClub (str): a specific guestClub name
                    homeClub (str): specific name of a homeClub
                Returns:
                    Returns homeClubWins/guestClubWins/draws (int)
                Example:
                    print(specificMatches("1. FC Nürnberg", "Hannover 96"))
            """
        guestClubWins = 0
        homeClubWins = 0
        draws = 0
        for i in fetchedMatches.index:
            if fetchedMatches["guestTeamName"][i] == guestClub and fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["homeScore"][i] < fetchedMatches["guestScore"][i]:
                guestClubWins = guestClubWins + 1
            if fetchedMatches["guestTeamName"][i] == guestClub and fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["homeScore"][i] == fetchedMatches["guestScore"][i]:
                  draws = draws + 1
            if fetchedMatches["guestTeamName"][i] == guestClub and fetchedMatches["homeTeamName"][i] == homeClub and fetchedMatches["homeScore"][i] > fetchedMatches["guestScore"][i]:
                homeClubWins = homeClubWins + 1
        result = [homeClubWins, guestClubWins, draws]
        return result


    def goalCountHome(homeClub):
        """saves every single goal count as homeClub as list
                        Args:
                            homeClub (str): specific name of a homeClub
                        Returns:
                            Resturns all goal counts list(int)
                        Example:
                            goalCountHome("1. FC Nürnberg")
                    """
        goalCount = []
        for i in fetchedMatches.index:
            if fetchedMatches["homeTeamName"][i] == homeClub:
                goalCount.append(fetchedMatches["homeScore"][i])
        return goalCount

    def goalCountGuest(guestClub):
        """saves every single goal count as guestClub as list
                            Args:
                                guestClub (str): specific name of a homeClub
                            Returns:
                                Resturns all goal counts list(int)
                            Example:
                                goalCountHome("1. FC Nürnberg")
                        """
        goalCount = []
        for i in fetchedMatches.index:
            if fetchedMatches["guestTeamName"][i] == guestClub:
                goalCount.append(fetchedMatches["guestScore"][i])
        return goalCount



    def createHistogram(axis, title, xAxis, yAxis, labels, values):
        """creates an histogram
                    Args:
                        axis (str):   position of the subplot
                        title (str):  title of the histogram
                        xAxis (str):  title of x Axis
                        yAxis (str):  title of y Axis
                        labels(array[str]): label name of each bar
                        values (array[int]):
                        maxY  (int):  max Value for y axis
                    Returns:
                        no returns
                    Example:
                        createHistogram(axes[0][0], "overall goals", "number of goals", "goal count", ["0","1","2","3","4"], ["0", "3", "8", "10", "5"])
                """
        axis.hist(values, color="black", rwidth=0.7, edgecolor="black", bins=range(0, 10))
        axis.set_xlabel(xAxis)
        axis.set_ylabel(yAxis)
        axis.set_title(title, fontdict={"fontsize": 15})


    def createBar(axis, title, xAxis, yAxis, labels, values, maxY):
        """creates a bar graph
                    Args:
                        axis (str):
                        title(str):   title of the histogram
                        xAxis (str):  title of x Axis
                        yAxis (str):  title of y Axis
                        labels(array[str]): label name of each bar
                        values(array[int]): values for the bar graph
                        maxY  (int):  max Value for y axis
                    Returns:
                        no returns
                    Example:
                        createBar(axes[0][0], "Matches as homeClub"," "," ", ["wins", "loses", "draws"], [0, 3, 8])
                """
        axis.bar(x=n.arange(0, 3), height=values, color="darkred", edgecolor="black", tick_label=labels, capsize=3)
        axis.set_xlabel(xAxis)
        axis.set_ylabel(yAxis)
        axis.set_ylim([0,maxY+10])
        axis.set_title(title, fontdict={"fontsize": 15})



    def statistics(homeClub, guestClub):
        """creates 6 diagrams for the choosen home and guest club and shows them
                    Args:
                        homeClub (str): specific name of a homeClub
                        guestClub (str): a specific guestClub name
                    Returns:
                        no returns
                    Example:
                        statistics("1. FC Nürnberg", "Hannover 96"))
                """
        fig, axes = pp.subplots(nrows=3,ncols=2, figsize=(20, 15))
        fig.suptitle("Statistics", fontsize=24)

        createBar(axes[0][0], "overall Matches by " + homeClub + " as home club", "", " ", ["wins", "loses", "draws"], matchResultsHome(homeClub), max(matchResultsHome(homeClub)))
        createBar(axes[0][1], "overall Matches by " + guestClub + " as guest club","", " ", ["wins", "loses", "draws"], matchResultsGuest(guestClub), max(matchResultsGuest(guestClub)))
        createBar(axes[1][0], "Results in the past", "", " ",[homeClub, guestClub, "draws"], specificMatches(homeClub, guestClub), max(specificMatches(homeClub, guestClub)))
        createBar(axes[1][1], "Results in the past", "", " ", [guestClub,homeClub, "draws"], specificMatches(guestClub, homeClub), max(specificMatches(homeClub, guestClub)))
        createHistogram(axes[2][0], "goals by " + homeClub + " as home club", "number of goals", "goal count", ["wins", "loses", "draws"], goalCountHome(homeClub))
        createHistogram(axes[2][1], "goals by " + guestClub + " as guest club", "number of goals", "goal count", ["wins", "loses", "draws"], goalCountGuest(guestClub))
        pp.show()

    statistics(homeClub,guestClub)

