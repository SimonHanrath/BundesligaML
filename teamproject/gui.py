import os
import sys
import requests.exceptions
from teamproject import crawler, data_analytics, models
# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMessageBox, QStyleFactory, QShortcut,
    QGridLayout, QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QCheckBox, QComboBox, QLabel, QPushButton)


class FuBaKI(QWidget):
    def __init__(self, parent=None):
        super(FuBaKI, self).__init__(parent)
        self.setWindowTitle('FuBaKI')
        self.init_elements()
        self.init_layout()
        self.init_content()
        self.selectAlgo.setCurrentIndex(1)
        self.init_style()
        # self.resize(775, 450)

    def init_elements(self):
        self.shortcutCloseWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        self.shortcutCloseWindow.activated.connect(self.close)

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
        self.selectFromSeason.currentIndexChanged.connect(self.change_from_season)
        self.selectFromDay.setEnabled(False)
        self.selectFromDay.addItem('Match Day')
        self.reset_items(self.selectFromDay)
        self.selectToLabel = QLabel('To')
        self.selectToSeason = QComboBox()
        self.selectToSeason.addItem('Season')
        self.reset_items(self.selectToSeason)
        self.selectToDay = QComboBox()
        self.selectToSeason.currentIndexChanged.connect(self.change_to_season)
        self.selectToDay.setEnabled(False)
        self.selectToDay.addItem('Match Day')
        self.reset_items(self.selectToDay)
        self.intvForceUpdate = QCheckBox('Force re-caching')
        self.crawlerButton = QPushButton('Fetch Data')
        self.crawlerButton.clicked.connect(self.crawlercall)

        self.trainingButton = QPushButton('Start Training')
        self.trainingButton.setEnabled(False)
        self.trainingButton.clicked.connect(self.trainingcall)

        self.selectTeamsLabel = QLabel('Pick teams for prediction:')
        self.selectHomeLabel = QLabel('Home')
        self.selectHomeTeam = QComboBox()
        self.selectHomeTeam.setEnabled(False)
        self.selectHomeTeam.addItem('Home Team')
        self.reset_items(self.selectHomeTeam)
        self.selectHomeTeam.currentIndexChanged.connect(self.change_home_team)
        self.selectGuestLabel = QLabel('Away')
        self.selectGuestTeam = QComboBox()
        self.selectGuestTeam.setEnabled(False)
        self.selectGuestTeam.addItem('Away Team')
        self.reset_items(self.selectGuestTeam)
        self.selectGuestTeam.currentIndexChanged.connect(self.change_guest_team)
        self.predictButton = QPushButton('Show Results')
        self.predictButton.clicked.connect(self.predict_result)
        self.predictButton.setEnabled(False)

        self.colon = QLabel()
        font = QFont('Times New Roman', 35, weight=QFont.Bold)
        self.colon.setFont(font)
        self.homeIcon = QLabel()
        self.guestIcon = QLabel()
        self.predictLabel = QLabel()
        self.statisticButton = QPushButton('More Statistics…')
        self.statisticButton.clicked.connect(self.statisticscall)
        self.statisticButton.setEnabled(False)

        self.nextMatchesLabel = QLabel('Upcoming matches:')
        self.nextMatches = QTableWidget()
        self.nextMatches.setMinimumWidth(280)
        self.nextMatches.setEditTriggers(QTableWidget.NoEditTriggers)
        self.nextMatches.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.nextMatches.clicked.connect(self.select_teams)
        self.nextMatches.setColumnCount(3)
        self.nextMatches.verticalHeader().setVisible(False)
        columnLabels = ['Date', 'Home Team', 'Away Team']
        self.nextMatches.setHorizontalHeaderLabels(columnLabels)
        self.nextMatches.setColumnWidth(0, 50)
        self.nextMatches.setColumnWidth(1, 150)
        self.nextMatches.setColumnWidth(2, 150)
        header = self.nextMatches.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

    def init_layout(self):
        rightUILayout = QGridLayout()
        spacing = QHBoxLayout()
        spacing.addSpacing(5)
        rightUILayout.addLayout(spacing, 0, 2)
        rightUILayout.setColumnStretch(1, 2)
        rightUILayout.setColumnStretch(2, 1)
        rightUILayout.setColumnStretch(3, 2)
        rightUILayout.addWidget(self.selectAlgoLabel, 0, 0, 1, 3)
        rightUILayout.addWidget(self.selectAlgo, 1, 0, 1, 2)
        rightUILayout.addWidget(QLabel(), 2, 0, 1, 3)
        rightUILayout.setRowStretch(2, 1)
        rightUILayout.addWidget(self.intvLabel, 3, 0, 1, 3)
        rightUILayout.addWidget(self.selectFromLabel, 4, 0)
        selectFromLayout = QHBoxLayout()
        selectFromLayout.addWidget(self.selectFromSeason)
        selectFromLayout.addWidget(self.selectFromDay)
        rightUILayout.addLayout(selectFromLayout, 4, 1)
        rightUILayout.addWidget(self.crawlerButton, 4, 3)
        rightUILayout.addWidget(self.selectToLabel, 5, 0)
        selectToLayout = QHBoxLayout()
        selectToLayout.addWidget(self.selectToSeason)
        selectToLayout.addWidget(self.selectToDay)
        rightUILayout.addLayout(selectToLayout, 5, 1)
        rightUILayout.addWidget(self.trainingButton, 5, 3)
        rightUILayout.addWidget(self.intvForceUpdate, 6, 1)
        rightUILayout.addWidget(QLabel(), 7, 0, 1, 3)
        rightUILayout.setRowStretch(7, 1)
        # rightUILayout.addWidget(QLabel(), 9, 0, 1, 3)
        # rightUILayout.setRowStretch(9, 1)
        rightUILayout.addWidget(self.selectTeamsLabel, 8, 0, 1, 3)
        rightUILayout.addWidget(self.selectHomeLabel, 9, 0)
        rightUILayout.addWidget(self.selectHomeTeam, 9, 1)
        rightUILayout.addWidget(self.predictButton, 9, 3)
        rightUILayout.addWidget(self.selectGuestLabel, 10, 0)
        rightUILayout.addWidget(self.selectGuestTeam, 10, 1)
        rightUILayout.addWidget(self.statisticButton, 10, 3)
        rightUILayout.addWidget(QLabel(), 11, 0, 1, 3)
        rightUILayout.setRowStretch(11, 1)
        iconLayout = QHBoxLayout()
        iconLayout.addStretch(1)
        iconLayout.addWidget(self.homeIcon)
        iconLayout.addWidget(self.colon)
        iconLayout.addWidget(self.guestIcon)
        iconLayout.addStretch(1)
        resultLayout = QVBoxLayout()
        resultLayout.addLayout(iconLayout)
        resultLayout.addWidget(self.predictLabel, Qt.AlignHCenter)
        rightUILayout.addLayout(resultLayout, 12, 0, 1, 2)

        leftUILayout = QVBoxLayout()
        leftUILayout.addWidget(self.nextMatchesLabel)
        leftUILayout.addWidget(self.nextMatches)

        ui = QHBoxLayout()
        ui.addLayout(leftUILayout, 2)
        ui.addSpacing(30)
        ui.addLayout(rightUILayout, 3)
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
        QLabel, QHeaderView, QTableView, QCheckBox {
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
            border: 1px solid rgb(236,236,236);
        } QPushButton:disabled {
            background: rgba(112,128,144,0.5);
        } QTableView {
            font-size: 10pt;
        }
        """
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setStyleSheet(styleSheet)

    def reset_items(self, box: QComboBox):
        """Clears all but the first item from a given Combobox.

        Args:
            box (QComboBox): Combobox that will be cleared.
        """
        label = box.itemText(0)
        box.clear()
        box.addItem(label, None)
        box.model().item(0).setEnabled(False)

    def reset_prediction(self):
        """Reset all elements involved in displaying prediction results.
        """
        self.predictButton.setEnabled(False)
        self.selectHomeTeam.setEnabled(False)
        self.selectGuestTeam.setEnabled(False)
        self.colon.setText('')
        self.predictLabel.setText('')
        self.homeIcon.setPixmap(QPixmap())
        self.guestIcon.setPixmap(QPixmap())
        self.statisticButton.setEnabled(False)

    def change_from_season(self, index: int):
        """Show available match days corresponding to the selected season, i.e.
        lower limit of the time interval.

        Args:
            index (int): Combobox index of the selected season.
        """
        season = self.selectFromSeason.itemData(index)
        matchdayIndex = self.selectFromDay.currentIndex()
        self.reset_items(self.selectFromDay)
        matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
        for day in range(1, matchdays + 1):
            self.selectFromDay.addItem(str(day), day)
        autoSelect = min(matchdayIndex, self.selectFromDay.count() - 1)
        self.selectFromDay.setCurrentIndex(autoSelect)
        self.selectFromDay.setEnabled(True)

    def change_to_season(self, index: int):
        """Show available match days corresponding to the selected season, i.e.
        upper limit of the time interval.

        Args:
            index (int): Combobox index of the selected season.
        """
        season = self.selectToSeason.itemData(index)
        matchdayIndex = self.selectToDay.currentIndex()
        self.reset_items(self.selectToDay)
        matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
        for day in range(1, matchdays + 1):
            self.selectToDay.addItem(str(day), day)
        autoSelect = min(matchdayIndex, self.selectToDay.count() - 1)
        self.selectToDay.setCurrentIndex(autoSelect)
        self.selectToDay.setEnabled(True)

    def change_algo(self, index):
        """Changing the prediction algorithm disables GUI elements and suggests
        a training data interval.

        Args:
            index (int): Combobox index of the selected prediction algorithm.
        """
        self.reset_prediction()
        algo = self.selectAlgo.itemData(index)
        numSeasons = self.avail['season'].count()
        if algo is not None and numSeasons > 0:
            if algo == 'baseline':
                self.select_interval(0, 8)
            elif algo == 'poisson':
                self.select_interval(2, 0)
            elif algo == 'dixoncoles':
                self.select_interval(numSeasons, 0)
                self.selectFromDay.setCurrentIndex(1)

    def select_interval(self, seasons: int, matchdays: int):
        """Automatically selects a given number of seasons and matchdays.

        Args:
            seasons (int): Number of seasons that shall be selected.
            matchdays (int): Number of match days that shall be selected.
        """
        assert seasons >= 0 and matchdays >= 0, \
            'Number of seasons and match days must be positive.'
        seasons = max(seasons - 1, 0)
        toSeasonLast = self.selectToSeason.count() - 1
        self.selectToSeason.setCurrentIndex(toSeasonLast)
        toDayLast = self.selectToDay.count() - 1
        self.selectToDay.setCurrentIndex(toDayLast)
        fromSeason = max(toSeasonLast - seasons, 1)
        self.selectFromSeason.setCurrentIndex(fromSeason)
        self.selectFromDay.setCurrentIndex(toDayLast)

        while matchdays > 0:
            matchdays -= 1
            toDayLast = self.selectFromDay.count() - 1
            if toDayLast - matchdays > 0:
                self.selectFromDay.setCurrentIndex(toDayLast - matchdays)
            elif fromSeason > 1:
                fromSeason -= 1
                matchdays += 1
                self.selectFromSeason.setCurrentIndex(fromSeason)
            else:
                matchdays = 0
                self.selectFromDay.setCurrentIndex(1)
            matchdays -= toDayLast

    def select_teams(self, item: QTableWidgetItem):
        """Automatically select corresponding teams for prediction after
        clicking on a row in next matches table.

        Args:
            item (QTableWidgetItem): The clicked item (i.e. table cell).
        """
        homeName = self.next.iloc[item.row()]['homeTeamName']
        guestName = self.next.iloc[item.row()]['guestTeamName']
        homeIndex = self.selectHomeTeam.findText(homeName, Qt.MatchExactly)
        guestIndex = self.selectGuestTeam.findText(guestName, Qt.MatchExactly)
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
        self.reset_items(self.selectHomeTeam)
        self.reset_items(self.selectGuestTeam)
        self.reset_prediction()
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
        if self.nextMatches.rowCount() > 0:
            self.select_teams(self.nextMatches.item(0, 0))
        self.predictButton.setEnabled(True)
        self.statisticButton.setEnabled(True)

    def predict_result(self):
        """Compute and display prediction results.
        """
        homeTeamID = self.selectHomeTeam.currentData()
        guestTeamID = self.selectGuestTeam.currentData()
        if None in (homeTeamID, guestTeamID):
            QMessageBox.warning(self, 'Invalid Teams', 'Please select a home and away team.')
            return  # exit
        elif homeTeamID == guestTeamID:
            QMessageBox.warning(self, 'Invalid Teams', 'Please select different home and away teams.')
            return  # exit

        # self.colon.setText(':')
        # homePixmap = self.display_teamicon(self.selectHomeTeam.currentData())
        # self.homeIcon.setPixmap(homePixmap)
        # guestPixmap = self.display_teamicon(self.selectGuestTeam.currentData())
        # self.guestIcon.setPixmap(guestPixmap)
        homeTeamName = str(self.selectHomeTeam.currentText())
        guestTeamName = str(self.selectGuestTeam.currentText())
        predictionList = self.model.predict(homeTeamName, guestTeamName)
        self.predictLabel.setText(f'Home: {round(predictionList[0]*100, 2)}%   '
                                  + f'Draw: {round(predictionList[1]*100, 2)}%   '
                                  + f'Away: {round(predictionList[2]*100, 2)}%')

    def change_home_team(self, index: int):
        """Display the selected home team's icon.

        Args:
            index (int): Combobox index of the selected home team.
        """
        homeTeamID = self.selectHomeTeam.itemData(index)
        if homeTeamID is not None:
            self.homeIcon.setPixmap(self.display_teamicon(homeTeamID))
            self.predictLabel.setText('')

    def change_guest_team(self, index: int):
        """Display the selected away team's icon.

        Args:
            index (int): Combobox index of the selected away team.
        """
        guestTeamID = self.selectHomeTeam.itemData(index)
        if guestTeamID is not None:
            self.guestIcon.setPixmap(self.display_teamicon(guestTeamID))
            self.predictLabel.setText('')

    def display_teamicon(self, team: int) -> QPixmap:
        """Display the icon of the home team selected for prediction.

        Args:
            team (int): The ID of the selected team.

        Returns:
            A QPixmap showing the desired team icon (or a dummy icon if image
            was not found).
        """
        self.colon.setText(':')
        iconURL = self.teamdata.loc[self.teamdata['ID'] == team, 'icon'].values[0]
        iconExtension = iconURL.split('.')[-1]
        iconPath = f'{crawler.g_cache_path}/teamicon.{iconExtension}'
        try:
            response = requests.get(iconURL, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout,
                requests.exceptions.ConnectionError):
            absPath = os.path.dirname(os.path.abspath(__file__))
            pixmap = QPixmap(f'{absPath}/none.svg')
        else:
            with open(iconPath, 'wb') as imageFile:
                imageFile.writelines(response.iter_content(1024))
            pixmap = QPixmap(iconPath)
        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        pixmap.setDevicePixelRatio(2.0)
        return pixmap

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
        homeTeamName = self.selectHomeTeam.currentText()
        guestTeamName = self.selectGuestTeam.currentText()
        data_analytics.main(self.matchdata, homeTeamName, guestTeamName)


def main():
    app = QApplication(sys.argv)
    absPath = os.path.dirname(os.path.abspath(__file__))
    app.setWindowIcon(QIcon(f'{absPath}/appicon.png'))
    app.setApplicationName('FuBaKI')
    window = FuBaKI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
