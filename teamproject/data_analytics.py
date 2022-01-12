import json

import pandas as pd

from crawler import fetch_data
from crawler import get_data
import matplotlib.pyplot as pp
import numpy as n


"""
The result is a list of matches. A match is a dict of the following structure:
{
    "date": "YYYY-MM-DDTHH:MM:SS",
    "homeClubId": int,
    "homeClub": str,
    "homeScore": int,
    "guestClubId": int,
    "guestClub": str,
    "guestScore": int
}
where "date" specifies the local date and time a match took place,
"homeClubId" and "guestClubId" represent the IDs of the home and visiting club,
"homeClub" and "guestClub" represent the full names of each club,
"homeScore" and "guestScore" represent the final goal score of each club.

ggf. weitere wichtige Daten: Liga; Ort; Tore (Spielminute, Torschütze,
Eigentor?, Strafe?, Verlängerung?); Wetter (von woanders)
"""

fetchedMatches = get_data(2009,180, 2021,140)
"""
Index(['date', 
       'homeClubId', 
       'homeClub',
       'guestClubId', 
       'guestClub',
       'homeScore', 
       'guestScore', 
       'goalMinsHome', 
       'goalMinsGuest', 
       'league'],
       dtype='object')
"""

#List of all teams without dupllicates
allTeams = []
duplicate = False
for i in fetchedMatches.index:

    for team in allTeams:
        if fetchedMatches["homeClub"][i] == team:
            duplicate = True
            break
        else:
            duplicate = False
    if duplicate == False:

        allTeams.append(fetchedMatches["homeClub"][i])

print(allTeams)


# wins by home team
homeWins =0
for i in fetchedMatches.index:
    if fetchedMatches["homeScore"][i] > fetchedMatches["guestScore"][i]:
        homeWins = homeWins+1
print("Heimspieltore: %s" % homeWins)

# wins by guest team
guestWins =0
for i in fetchedMatches.index:
    if fetchedMatches["homeScore"][i] < fetchedMatches["guestScore"][i]:
        guestWins = guestWins+1
print("Gastpieltore: %s" % guestWins)

# draw matches
drawMatches =0
for i in fetchedMatches.index:
    if fetchedMatches["homeScore"][i] == fetchedMatches["guestScore"][i]:
        drawMatches = drawMatches+1
print("Unenschieden Tore: %s" % drawMatches)


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
        if fetchedMatches["homeClub"][i] == homeClub and fetchedMatches["homeScore"][i] > fetchedMatches["guestScore"][i]:
            wins = wins + 1
        if fetchedMatches["homeClub"][i] == homeClub and fetchedMatches["homeScore"][i] == fetchedMatches["guestScore"][i]:
            loses = loses + 1
        if fetchedMatches["homeClub"][i] == homeClub and fetchedMatches["homeScore"][i] < fetchedMatches["guestScore"][i]:
            draws = draws + 1
    result = [wins, loses, draws]
    return result

   # print(homeClub + " : %s" % wins)
   # print(homeClub + " : %s" % loses)
   # print(homeClub + " : %s" % draws)



#print("machtes of each team as homeClub: ")
#for team in allTeams:
#    matchResultsHome(team)


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
        if fetchedMatches["guestClub"][i] == guestClub and fetchedMatches["guestScore"][i] > fetchedMatches["homeScore"][i]:
            wins = wins + 1
        if fetchedMatches["guestClub"][i] == guestClub and fetchedMatches["guestScore"][i] == fetchedMatches["homeScore"][i]:
            loses = loses + 1
        if fetchedMatches["guestClub"][i] == guestClub and fetchedMatches["guestScore"][i] < fetchedMatches["homeScore"][i]:
            draws = draws + 1
    result = [wins, loses, draws]
    return result

   # print(guestClub + " : %s" % wins)
   #  print(guestClub + " : %s" % loses)
   # print(guestClub + " : %s" % draws)

#print("machtes of each team as guestClub: ")
#for team in allTeams:
#    matchResultsGuest(team)


def specificMatchesHome (homeClub):
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
            if fetchedMatches["homeClub"][i] == homeClub and fetchedMatches["guestClub"][i] == team and fetchedMatches["guestScore"][i] < fetchedMatches["homeScore"][i]:
                wins = wins +1
            if fetchedMatches["homeClub"][i] == homeClub and fetchedMatches["guestClub"][i] == team and fetchedMatches["guestScore"][i] == fetchedMatches["homeScore"][i]:
                draws = draws +1
            if fetchedMatches["homeClub"][i] == homeClub and fetchedMatches["guestClub"][i] == team and fetchedMatches["guestScore"][i] > fetchedMatches["homeScore"][i]:
                loses = loses +1
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

   #  print("As homeClub " + homeClub + " wins the most times against: " + accWinsName)
   #  print(homeClub + " has won %s" % accWins + " times against " + accWinsName)
   # print("As homeClub " + homeClub + " loses the most times against: " + accLosesName)
   # print(homeClub + " has lost %s" % accLoses + " times against " + accLosesName)
   # print("As homeClub " + homeClub + " draws the most times against: " + accDrawsName)
   # print(homeClub + " draws %s" % accDraws + " times against " + accDrawsName)

# testing with "FC Bayern München"
#specificMatchesHome("FC Bayern München")

def specificMatchesGuest (guestClub):
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
            if fetchedMatches["homeClub"][i] == guestClub and fetchedMatches["homeClub"][i] == team and fetchedMatches["homeScore"][i] < fetchedMatches["guestScore"][i]:
                wins = wins +1
            if fetchedMatches["homeClub"][i] == guestClub and fetchedMatches["homeClub"][i] == team and fetchedMatches["homeScore"][i] == fetchedMatches["guestScore"][i]:
                draws = draws +1
            if fetchedMatches["homeClub"][i] == guestClub and fetchedMatches["homeClub"][i] == team and fetchedMatches["homeScore"][i] > fetchedMatches["guestScore"][i]:
                loses = loses +1
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
   # print("As guestClub " + guestClub + " wins the most times against: " + accWinsName)
  #  print(guestClub + " has won %s" % accWins + " times against " + accWinsName)
   # print("As guestClub " + guestClub + " loses the most times against: " + accLosesName)
   # print(guestClub + " has lost %s" % accLoses + " times against " + accLosesName)
   # print("As guestClub " + guestClub + " draws the most times against: " + accDrawsName)
   # print(guestClub + " draws %s" % accDraws + " times against " + accDrawsName)

# testing with "FC Bayern München"
#specificMatchesGuest("FC Bayern München")


def createHistogram(axis,  title, xAxis, yAxis, labels, values ):
    """creates an histogram

                Args:
                    axis (str):   position of the subplot
                    title (str):  title of the histogram
                    xAxis (str):  title of x Axis
                    yAxis (str):  title of y Axis
                    labels(array[str]): label name of each bar
                    values (array[int]):

                Returns:
                    no returns

                Example:
                    createHistogram(axes[0][0], "overall goals","number of goals", "goal count",["0","1","2","3","4"], [0, 3, 8 ,10 , 5])
            """
    axis.hist(values, color="black", rwidth=0.7, edgecolor="black", bins= range(0, 10))
    axis.set_xlabel(xAxis)
    axis.set_ylabel(yAxis)
    axis.set_title(title, fontdict={"fontsize": 18})

def createBar(axis, title, xAxis, yAxis, labels, values):
    """creates a bar graph

                Args:
                    axis (str):
                    title(str):   title of the histogram
                    xAxis (str):  title of x Axis
                    yAxis (str):  title of y Axis
                    labels(array[str]): label name of each bar
                    values(array[int]): values for the bar graph

                Returns:
                    no returns

                Example:
                    createBar(axes[0][0], "Matches as homeClub"," "," ", ["wins", "loses", "draws"], [0, 3, 8])
            """
    axis.bar(x=n.arange(0,3),height=values,color="darkred", edgecolor="black", tick_label=labels, capsize=3)
    axis.set_xlabel(xAxis)
    axis.set_ylabel(yAxis)
    axis.set_title(title, fontdict={"fontsize": 18})


#testing graphs
fig,axes=pp.subplots(1,2, figsize=(15,8))
fig.suptitle("Examples", fontsize=24)
createHistogram(axes[0],"overall goals","number of goals", "goal count", ["wins", "loses", "draws"], abs(n.random.normal(size=1000)))
createBar(axes[1], "Matches as homeClub","FC Bayern München "," ", ["wins", "loses", "draws"], matchResultsHome("FC Bayern München"))
pp.show()