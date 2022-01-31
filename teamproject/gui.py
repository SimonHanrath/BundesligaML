# -*- coding: utf-8 -*-
import os
import sys
import urllib.request
from teamproject import crawler, data_analytics, models
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtSvg import QSvgWidget
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QWidget,
    QShortcut,
    QMessageBox,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QStyleFactory
)


class FuBaKI(QWidget):
    def __init__(self, parent=None):
        super(FuBaKI, self).__init__(parent)
        self.setWindowTitle('FuBaKI')
        self.init_elements()
        self.init_layout()
        self.init_content()
        self.init_style()
        self.resize(1000, 700)

    def init_elements(self):
        self.shortcutQuit = QShortcut(QtGui.QKeySequence('Ctrl+Q'), self)
        self.shortcutQuit.activated.connect(self.close)
        self.shortcutClose = QShortcut(QtGui.QKeySequence('Ctrl+W'), self)
        self.shortcutClose.activated.connect(self.close)

        self.selectAlgoLabel = QLabel('Select the desired algorithm:')
        self.selectAlgo = QComboBox()
        self.selectAlgo.addItem('Prediction Algorithm')
        self.reset_items(self.selectAlgo)
        self.selectAlgo.addItem('Baseline Algorithm', 'baseline')
        self.selectAlgo.addItem('Poisson Regression', 'poisson')
        self.selectAlgo.addItem('Dixon Coles Algorithm', 'dixoncoles')
        self.selectAlgo.currentIndexChanged.connect(self.change_algo)

        self.intvLabel = QLabel('Specify the interval of training data:')
        self.selectFromLabel = QLabel('From')
        self.selectFromSeason = QComboBox()
        self.selectFromSeason.addItem('Season')
        self.reset_items(self.selectFromSeason)
        self.selectFromDay = QComboBox()
        self.selectFromSeason.currentIndexChanged.connect(self.fill_from_day)
        self.selectFromDay.setEnabled(False)
        self.selectFromDay.addItem('Match Day')
        self.reset_items(self.selectFromDay)
        self.selectToLabel = QLabel('To')
        self.selectToSeason = QComboBox()
        self.selectToSeason.addItem('Season')
        self.reset_items(self.selectToSeason)
        self.selectToDay = QComboBox()
        self.selectToSeason.currentIndexChanged.connect(self.fill_to_day)
        self.selectToDay.setEnabled(False)
        self.selectToDay.addItem('Match Day')
        self.reset_items(self.selectToDay)
        self.intvForceUpdate = QCheckBox('force re-caching')
        self.crawlerButton = QPushButton('Fetch Data')
        self.crawlerButton.clicked.connect(self.crawlercall)

        self.trainingButton = QPushButton('Start Training')
        self.trainingButton.setEnabled(False)
        self.trainingButton.clicked.connect(self.trainingcall)

        self.selectTeamsLabel = QLabel('Pick teams for prediction:')
        self.selectHomeTeam = QComboBox()
        self.selectHomeTeam.setEnabled(False)
        self.selectHomeTeam.addItem('Home Team')
        self.reset_items(self.selectHomeTeam)
        self.selectGuestTeam = QComboBox()
        self.selectGuestTeam.setEnabled(False)
        self.selectGuestTeam.addItem('Guest Team')
        self.reset_items(self.selectGuestTeam)
        self.predictButton = QPushButton('Show Results')
        self.predictButton.clicked.connect(self.resultscall)
        self.predictButton.setEnabled(False)

        self.colon = QLabel()
        font = QtGui.QFont('Times New Roman', 35, weight=QtGui.QFont.Bold)
        self.colon.setFont(font)
        self.homeIcon = QLabel()
        self.guestIcon = QLabel()
        self.resultLabel = QLabel()
        self.statisticButton = QPushButton('More Statistics…')
        self.statisticButton.clicked.connect(self.statisticscall)
        self.statisticButton.setEnabled(False)

        self.nextMatchesLabel = QLabel('Upcoming matches:')
        self.nextMatches = QTableWidget()
        self.nextMatches.setMinimumWidth(250)
        self.nextMatches.setEditTriggers(QTableWidget.NoEditTriggers)
        self.nextMatches.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.nextMatches.doubleClicked.connect(self.select_teams)
        self.nextMatches.setColumnCount(3)
        self.nextMatches.verticalHeader().setVisible(False)
        columnLabels = ['Date', 'Home Team', 'Guest Team']
        self.nextMatches.setHorizontalHeaderLabels(columnLabels)
        self.nextMatches.setColumnWidth(0, 50)
        self.nextMatches.setColumnWidth(1, 150)
        self.nextMatches.setColumnWidth(2, 150)
        header = self.nextMatches.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    def init_layout(self):
        algoLayout = QHBoxLayout()
        algoLayout.addWidget(self.selectAlgo, 1)
        algoLayout.addStretch(2)
        intvLayout = QHBoxLayout()
        intvLayout.addWidget(self.selectFromLabel)
        intvLayout.addWidget(self.selectFromSeason, 1)
        intvLayout.addWidget(self.selectFromDay, 1)
        intvLayout.addSpacing(25)
        intvLayout.addWidget(self.selectToLabel)
        intvLayout.addWidget(self.selectToSeason, 1)
        intvLayout.addWidget(self.selectToDay, 1)
        recacheLayout = QHBoxLayout()
        recacheLayout.addWidget(self.intvForceUpdate)
        recacheLayout.addSpacing(25)
        recacheLayout.addWidget(self.crawlerButton, 1)
        recacheLayout.addStretch(2)
        trainingLayout = QHBoxLayout()
        trainingLayout.addWidget(self.trainingButton, 1)
        trainingLayout.addStretch(2)
        iconLayout = QHBoxLayout()
        iconLayout.addStretch(1)
        iconLayout.addWidget(self.homeIcon)
        iconLayout.addSpacing(10)
        iconLayout.addWidget(self.colon)
        iconLayout.addSpacing(10)
        iconLayout.addWidget(self.guestIcon)
        iconLayout.addStretch(3)
        predictLayout = QHBoxLayout()
        predictLayout.addWidget(self.selectHomeTeam, 2)
        predictLayout.addWidget(self.selectGuestTeam, 2)
        predictLayout.addSpacing(25)
        predictLayout.addWidget(self.predictButton, 1)
        resultLayout = QHBoxLayout()
        resultLayout.addStretch(1)
        resultLayout.addWidget(self.resultLabel)
        resultLayout.addStretch(4)
        statisticLayout = QHBoxLayout()
        statisticLayout.addWidget(self.statisticButton, 1)
        statisticLayout.addStretch(2)

        leftUILayout = QVBoxLayout()
        leftUILayout.addWidget(self.selectAlgoLabel)
        leftUILayout.addLayout(algoLayout)
        leftUILayout.addStretch(3)
        leftUILayout.addWidget(self.intvLabel)
        leftUILayout.addLayout(intvLayout)
        leftUILayout.addSpacing(5)
        leftUILayout.addLayout(recacheLayout)
        leftUILayout.addStretch(1)
        leftUILayout.addLayout(trainingLayout)
        leftUILayout.addStretch(3)
        leftUILayout.addWidget(self.selectTeamsLabel)
        leftUILayout.addLayout(predictLayout)
        leftUILayout.addStretch(1)
        leftUILayout.addLayout(iconLayout)
        leftUILayout.addLayout(resultLayout)
        leftUILayout.addStretch(1)
        leftUILayout.addLayout(statisticLayout)
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.nextMatchesLabel)
        rightLayout.addWidget(self.nextMatches)

        ui = QHBoxLayout()
        ui.addLayout(leftUILayout, 2)
        ui.addSpacing(50)
        ui.addLayout(rightLayout, 1)
        self.setLayout(ui)

    def init_content(self):
        crawler.refresh_ui_cache()
        self.avail = crawler.load_cache_index()
        self.next = crawler.load_matchdata('next')

        for season in self.avail['season'].values:
            self.selectFromSeason.addItem(str(season), season)
            self.selectToSeason.addItem(str(season), season)

        nextMatchdata = self.next.to_dict('records')
        self.nextMatches.setRowCount(len(nextMatchdata))
        for i in range(0, len(nextMatchdata)):
            date = nextMatchdata[i]['datetime'].strftime('%d %b, %H:%M ')
            homeTeamName = nextMatchdata[i]['homeTeamName']
            guestTeamName = nextMatchdata[i]['guestTeamName']
            self.nextMatches.setItem(i, 0, QTableWidgetItem(date))
            self.nextMatches.setItem(i, 1, QTableWidgetItem(homeTeamName))
            self.nextMatches.setItem(i, 2, QTableWidgetItem(guestTeamName))

    def init_style(self):
        styleSheet = """
        QLabel, QHeaderView, QTableView {
            color: rgb(55,65,74);
        } QPushButton {
            background: rgb(112,128,144);
            border: none;
            border-radius: 3px;
            color: rgb(255,255,255);
            font-weight: bold;
            padding: 7px 10px;
        } QPushButton:hover {
            background: rgb(119,136,153);
        } QPushButton:pressed {
            background: rgb(55,65,74);
            border: 1px solid rgb(255,255,255);
        } QPushButton:disabled {
            background: rgba(112,128,144,0.5);
        } QTableView {
            font-size: 10pt;
        }
        """
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setStyleSheet(styleSheet)

    def reset_items(self, box):
        """Clears all but the first item from a given Combobox.

        Args:
            box (QComboBox): Combobox that will be cleared.
        """
        label = box.itemText(0)
        box.clear()
        box.addItem(label, None)
        box.model().item(0).setEnabled(False)

    def fill_from_day(self, index):
        """Show available match days corresponding to the selected season, i.e.
        lower limit of the time interval.

        Args:
            index (int): Combobox index of the selected season.
        """
        self.reset_items(self.selectFromDay)
        season = self.selectFromSeason.itemData(index)
        matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
        for day in range(1, matchdays + 1):
            self.selectFromDay.addItem(str(day), day)
        self.selectFromDay.setCurrentIndex(1)
        self.selectFromDay.setEnabled(True)

    def fill_to_day(self, index):
        """Show available match days corresponding to the selected season, i.e.
        upper limit of the time interval.

        Args:
            index (int): Combobox index of the selected season.
        """
        self.reset_items(self.selectToDay)
        season = self.selectToSeason.itemData(index)
        matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
        for day in range(1, matchdays + 1):
            self.selectToDay.addItem(str(day), day)
        self.selectToDay.setCurrentIndex(matchdays)
        self.selectToDay.setEnabled(True)

    def change_algo(self, index):
        """Changing the prediction algorithm disables GUI elements and suggests
        a training data interval.

        Args:
            index (int): Combobox index of the selected prediction algorithm.
        """
        self.selectHomeTeam.setEnabled(False)
        self.selectGuestTeam.setEnabled(False)
        self.predictButton.setEnabled(False)
        self.statisticButton.setEnabled(False)

        algo = self.selectAlgo.itemData(index)
        toSeasonLast = self.selectToSeason.count() - 1
        if algo is not None and toSeasonLast > 0:
            self.selectToSeason.setCurrentIndex(toSeasonLast)
            if algo == 'baseline':
                days = 7
                fromSeason = toSeasonLast
                while days > 0 and fromSeason > 1:
                    self.selectFromSeason.setCurrentIndex(fromSeason)
                    toDayLast = self.selectFromDay.count() - 1
                    if toDayLast - days > 0:
                        self.selectFromDay.setCurrentIndex(toDayLast - days)
                    else:
                        fromSeason = fromSeason - 1
                    days = days - toDayLast
            elif algo == 'poisson':
                fromSeason = self.clamp(toSeasonLast - 2, 1)
                self.selectFromSeason.setCurrentIndex(fromSeason)
                toDayLast = self.selectToDay.count() - 1
                self.selectFromDay.setCurrentIndex(self.clamp(toDayLast, 1))
            elif algo == 'dixoncoles':
                self.selectFromSeason.setCurrentIndex(1)

    def clamp(self, num: int, min: int):
        """Clamps a number to a given minimum.

        Args:
            num (int): An arbitrary number.
            min (int): The desired minimum.

        Returns:
            Resulting number, clamped to the given minimum
        """
        if num < 0:
            return 0
        else:
            return num

    def select_teams(self):
        """After double clicking on a row in next matches table, automatically
        select corresponding teams for prediction.
        """
        row = self.nextMatches.currentRow()
        homeName = self.next.iloc[row]['homeTeamName']
        guestName = self.next.iloc[row]['guestTeamName']
        homeIndex = self.selectHomeTeam.findText(homeName, QtCore.Qt.MatchFixedString)
        guestIndex = self.selectGuestTeam.findText(guestName, QtCore.Qt.MatchFixedString)
        if homeIndex >= 0 and self.selectHomeTeam.isEnabled():
            self.selectHomeTeam.setCurrentIndex(homeIndex)
        if guestIndex >= 0 and self.selectGuestTeam.isEnabled():
            self.selectGuestTeam.setCurrentIndex(guestIndex)

    def crawlercall(self):
        """Fetches data within the chosen time interval. After that, fills
        home team and guest team comboboxes with teams names.
        """
        self.crawlerButton.setEnabled(False)
        self.selectHomeTeam.setEnabled(False)
        self.selectGuestTeam.setEnabled(False)
        self.trainingButton.setEnabled(False)
        self.predictButton.setEnabled(False)
        self.statisticButton.setEnabled(False)
        self.reset_items(self.selectHomeTeam)
        self.reset_items(self.selectGuestTeam)
        fromSeason = self.selectFromSeason.currentData()
        fromDay = self.selectFromDay.currentData()
        toSeason = self.selectToSeason.currentData()
        toDay = self.selectToDay.currentData()
        forceUpdate = self.intvForceUpdate.isChecked()

        if None in (fromSeason, fromDay, toSeason, toDay):
            message = 'Selected interval incomplete.'
            QMessageBox.warning(self, 'Invalid interval', message)
        elif (fromSeason == toSeason and fromDay > toDay) or (fromSeason > toSeason):
            message = 'Please select a valid time interval.'
            QMessageBox.warning(self, 'Invalid interval', message)
        else:
            self.matchdata = crawler.get_data(fromSeason, fromDay, toSeason, toDay, forceUpdate)
            self.teamdata = crawler.get_teams(self.matchdata)
            teamList = self.teamdata.to_dict('records')
            for team in teamList:
                self.selectHomeTeam.addItem(team['name'], team['ID'])
                self.selectGuestTeam.addItem(team['name'], team['ID'])
            self.trainingButton.setEnabled(True)

        self.crawlerButton.setEnabled(True)

    def trainingcall(self):
        """Train chosen algorithm on the basis of selected time interval.
        """
        algo = self.selectAlgo.currentData()
        if algo is None:
            message = 'Please select an algorithm.'
            QMessageBox.warning(self, 'No algorithm selected', message)
            return  # exit
        elif algo == 'baseline':
            self.model = models.BaselineAlgo(self.matchdata)
        elif algo == 'poisson':
            self.model = models.PoissonRegression(self.matchdata)
        elif algo == 'dixoncoles':
            self.model = models.DixonColes(self.matchdata)

        self.selectHomeTeam.setEnabled(True)
        self.selectGuestTeam.setEnabled(True)
        self.predictButton.setEnabled(True)
        self.statisticButton.setEnabled(True)

    def resultscall(self):
        """Compute and display prediction results.
        """
        homeTeamID = self.selectHomeTeam.currentData()
        guestTeamID = self.selectGuestTeam.currentData()
        if None in (homeTeamID, guestTeamID):
            QMessageBox.warning(self, 'Invalid Teams', 'Please select a home and guest team.')
            return  # exit
        elif homeTeamID == guestTeamID:
            QMessageBox.warning(self, 'Invalid Teams', 'Please select different home and guest teams.')
            return  # exit

        self.colon.setText(':')
        self.display_home_icon()
        self.display_guest_icon()
        homeTeamName = str(self.selectHomeTeam.currentText())
        guestTeamName = str(self.selectGuestTeam.currentText())
        predictionList = self.model.predict(homeTeamName, guestTeamName)
        self.resultLabel.setText(f'home: {str(round(predictionList[0]*100, 2))}%   '
                                 + f'draw: {str(round(predictionList[1]*100, 2))}%   '
                                 + f'guest: {str(round(predictionList[2]*100, 2))}%')

    def display_guest_icon(self):
        """Display the icon of the guest team selected for prediction.
        """
        guestIcon = self.teamdata.loc[self.teamdata['ID'] == self.selectGuestTeam.currentData(), 'icon'].values[0]
        guestIconPath = f'{crawler.g_cache_path}/guestIcon.png'
        urllib.request.urlretrieve(guestIcon, guestIconPath)
        pixmap = QtGui.QPixmap(guestIconPath)
        self.guestIcon.setPixmap(pixmap.scaled(100, 100))

    def display_home_icon(self):
        """Display the icon of the home team selected for prediction.
        """
        homeIcon = self.teamdata.loc[self.teamdata['ID'] == self.selectHomeTeam.currentData(), 'icon'].values[0]
        homeIconPath = f'{crawler.g_cache_path}/homeIcon.png'
        urllib.request.urlretrieve(homeIcon, homeIconPath)
        pixmap = QtGui.QPixmap(homeIconPath)
        self.homeIcon.setPixmap(pixmap.scaled(100, 100))

    def display_icon(self):
        """TO-DO
        """
        pass

    def statisticscall(self):
        """Open window with detailed statistics.
        """
        homeTeamID = self.selectHomeTeam.currentData()
        guestTeamID = self.selectGuestTeam.currentData()
        if None in (homeTeamID, guestTeamID):
            QMessageBox.warning(self, 'Invalid Teams', 'Please select a home and guest team.')
            return  # exit
        elif homeTeamID == guestTeamID:
            QMessageBox.warning(self, 'Invalid Teams', 'Please select different home and guest teams.')
            return  # exit
        data_analytics.main(self.matchdata, self.selectHomeTeam.currentText(), self.selectGuestTeam.currentText())


def main():
    app = QApplication(sys.argv)
    path = {os.path.dirname(os.path.abspath(__file__))}
    app.setWindowIcon(QtGui.QIcon(f'{path}/img/icon.png'))
    window = FuBaKI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
