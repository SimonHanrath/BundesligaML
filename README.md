FubaKI
-----------

FubaKI is a Bundesliga prediction programm. It allows anyone to predict the results of upcoming matches with machine learning algorithms.
The Programm allows you to choose between different algorithms to predict the outcome of the chosen game. You can choose between the
Baseline algorithm, Poisson Regression Algorithm and the Dixon Coles Algorithm. Because each of those algorithmes has different properties,
the chosen Timeframe for the crawled data can greatly impact the outcome. Because of this reason, here is a suggestet timeframe for each of the 
Algorithmes.

Baseline Algorithm: Previous 8 Days

PoissonRegression: Previous 2 Seasons

Dixon Coles: Largest Possible timeframe

<img src="fuba.png">


Dependencies
=====

FubaKI supports Python 3.8+ .

Installation requires numpy, matplotlib, aiohttp, asyncio, statsmodels, pandas and pyQT5.

Installation
============

1. Clone this reposetory to your device

2. Install the needed packages

3. Execute the "main.py" file

