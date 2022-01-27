import sys
import urllib.request
import pandas as pd
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtSvg import QSvgWidget
# -*- coding: utf-8 -*-
#from svglib.svglib import svg2rlg
#from reportlab.graphics import renderPM

from PyQt5.QtWidgets import QWidget, QMessageBox, QHBoxLayout, QComboBox, QVBoxLayout, QCheckBox, QPushButton, QLabel
from teamproject import crawler
from teamproject import data_analytics
from teamproject.models import BaselineAlgo
from teamproject.models import DixonColes
from teamproject.models import PoissonRegression



def main():
    """
    Creates and shows the main window.
    """
    class Ui_Dialog(QWidget):

        def setupUi(self, Dialog):
            """
            Define all the Ui Elements in this method.

            Args:
                Dialog (QDialog): Main window
            """
            #super().__init__()
            Dialog.setMinimumSize(1355, 841)
            Dialog.resize(1355, 841)

            # create the ok and cancel buttons
            self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
            self.buttonBox.setGeometry(QtCore.QRect(1000, 800, 341, 32))
            self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
            self.buttonBox.setObjectName('buttonBox')

            # create a button to show the upcoming playday
            self.playdayButton = QPushButton(Dialog)
            self.playdayButton.setGeometry(QtCore.QRect(550, 90, 230, 60))
            self.playdayButton.setObjectName('Show upcoming matches')
            self.playdayButton.clicked.connect(self.playdaycall)

            # select the Algo label, to change the text have a look at the retranslateUi function
            self.playdayLabel = QLabel(Dialog)
            self.playdayLabel.setGeometry(QtCore.QRect(950, 30, 323, 590))
            self.playdayLabel.setObjectName('playdayLabel')

            # select the Algo label, to change the text have a look at the retranslateUi function
            self.selectAlgoLabel = QLabel(Dialog)
            self.selectAlgoLabel.setGeometry(QtCore.QRect(30, 30, 371, 31))
            self.selectAlgoLabel.setObjectName('selectAlgoLabel')

            # selectAlgo: Select the algorithm you want to use
            self.selectAlgo = QComboBox(Dialog)
            self.selectAlgo.setGeometry(QtCore.QRect(40, 90, 301, 60))
            self.selectAlgo.setObjectName('selectAlgo')
            self.selectAlgo.addItem('Baseline Algorithm')
            self.selectAlgo.addItem('Poisson Regression')
            self.selectAlgo.addItem('Dixon Coles Algorithm')
            self.selectAlgo.currentIndexChanged.connect(self.change_algo)

            # A label that tells you to select the start time, to change the text have a look at the retranslateUi function
            self.selectStartTimeLabel = QLabel(Dialog)
            self.selectStartTimeLabel.setGeometry(QtCore.QRect(30, 180, 371, 31))
            self.selectStartTimeLabel.setObjectName('selectStartTimeLabel')

            # A label that tells you to select the end time, to change the text have a look at the retranslateUi function
            self.selectEndTimeLabel = QLabel(Dialog)
            self.selectEndTimeLabel.setGeometry(QtCore.QRect(450, 180, 371, 31))
            self.selectEndTimeLabel.setObjectName('selectEndTimeLabel')

            # The combobox to select the start season
            self.selectFromYear = QComboBox(Dialog)
            self.selectFromYear.setGeometry(QtCore.QRect(40, 250, 104, 87))
            self.selectFromYear.setObjectName('selectFromYear')
            self.selectFromYear.addItem('SelectStartSeasonLabel')
            self.reset_items(self.selectFromYear)

            # The combobox to select the start match day
            self.selectFromDay = QComboBox(Dialog)
            self.selectFromDay.setGeometry(QtCore.QRect(160, 250, 104, 87))
            self.selectFromDay.setObjectName('selectFromDay')
            self.selectFromDay.setEnabled(False)
            self.selectFromDay.addItem('SelectStartMatchdayLabel')
            self.reset_items(self.selectFromDay)

            # The combobox to select the end season
            self.selectToYear = QComboBox(Dialog)
            self.selectToYear.setGeometry(QtCore.QRect(450, 250, 104, 87))
            self.selectToYear.setObjectName('selectToYear')
            self.selectToYear.addItem('SelectEndSeasonLabel')
            self.reset_items(self.selectToYear)

            # The combobox to select the end match day
            self.selectToDay = QComboBox(Dialog)
            self.selectToDay.setGeometry(QtCore.QRect(570, 250, 104, 87))
            self.selectToDay.setObjectName('selectToDay')
            self.selectToDay.setEnabled(False)
            self.selectToDay.addItem('SelectEndMatchdayLabel')
            self.reset_items(self.selectToDay)

            # force update flag
            self.forceUpdateBox = QCheckBox(Dialog)
            self.forceUpdateBox.setGeometry(QtCore.QRect(40, 310, 30, 30))
            self.forceUpdateLabel = QLabel(Dialog)
            self.forceUpdateLabel.setGeometry(QtCore.QRect(60, 310, 100, 31))
            self.forceUpdateLabel.setObjectName('forceUpdateLabel')
            self.forceUpdateLabel.mousePressEvent = self.toggle_force_update

            # activate crawler Button
            self.crawlerButton = QPushButton(Dialog)
            self.crawlerButton.setGeometry(QtCore.QRect(40, 350, 331, 101))
            self.crawlerButton.setObjectName('Activate Crawler')
            self.crawlerButton.clicked.connect(self.crawlercall)

            # a label that tells you to select the team, to change the text have a look at the retranslateUi function
            self.selectTeamsLabel = QLabel(Dialog)
            self.selectTeamsLabel.setGeometry(QtCore.QRect(30, 480, 371, 31))
            self.selectTeamsLabel.setObjectName('selectTeamsLabel')

            # the combobox to select the home team
            self.selectHomeTeam = QComboBox(Dialog)
            self.selectHomeTeam.setGeometry(QtCore.QRect(40, 530, 301, 61))
            self.selectHomeTeam.setObjectName('selectHomeTeam')
            self.selectHomeTeam.setEnabled(False)
            self.selectHomeTeam.addItem('SelectHomeTeamLabel')
            self.reset_items(self.selectHomeTeam)

            # the combobox to select the guest team
            self.selectGuestTeam = QComboBox(Dialog)
            self.selectGuestTeam.setGeometry(QtCore.QRect(570, 530, 301, 61))
            self.selectGuestTeam.setObjectName('selectGuestTeam')
            self.selectGuestTeam.setEnabled(False)
            self.selectGuestTeam.addItem('SelectGuestTeamLabel')
            self.reset_items(self.selectGuestTeam)

            # A label of colon between Team Icons
            self.colon = QLabel(Dialog)
            self.colon.setGeometry(QtCore.QRect(1100, 180, 20, 61))
            self.colon.setObjectName(':')

            # A label that shows home Team Icon
            self.homeIcon = QLabel(Dialog)
            self.homeIcon.setGeometry(980,150, 100, 100)
            self.homeIcon.setObjectName('homeIcon')
            self.homeIcon.setText("")

            # A label that shows guest Team Icon
            self.guestIcon = QLabel(Dialog)
            self.guestIcon.setGeometry(1130, 150, 100, 100)
            self.guestIcon.setObjectName('guestIcon')
            self.guestIcon.setText("")

            # start training button
            self.trainingButton = QPushButton(Dialog)
            self.trainingButton.setGeometry(QtCore.QRect(100, 660, 331, 101))
            self.trainingButton.setObjectName('Start training')
            self.trainingButton.clicked.connect(self.trainingcall)
            self.trainingButton.setEnabled(False)

            # show result button
            self.predictButton = QPushButton(Dialog)
            self.predictButton.setGeometry(QtCore.QRect(430, 660, 331, 101))
            self.predictButton.setObjectName('Show results')
            self.predictButton.clicked.connect(self.resultscall)
            self.predictButton.setEnabled(False)

            # this label will show the results
            self.resultLabel = QLabel(Dialog)
            self.resultLabel.setGeometry(QtCore.QRect(1000, 250, 371, 31))
            self.resultLabel.setObjectName('resultLabel')

            # show statistic button
            self.statisticbutton = QPushButton(Dialog)
            self.statisticbutton.setGeometry(QtCore.QRect(1100, 660, 90, 30))
            self.statisticbutton.setObjectName('more statistics')
            self.statisticbutton.clicked.connect(self.statisticscall)
            self.statisticbutton.setEnabled(False)

            # call the retranslate
            self.retranslateUi(Dialog)

            # ok and cancel button
            self.buttonBox.accepted.connect(Dialog.accept)
            self.buttonBox.rejected.connect(Dialog.reject)

            QtCore.QMetaObject.connectSlotsByName(Dialog)

            # load available data
            #crawler.refresh_ui_cache() TO-DO: uncomment
            self.avail = crawler.load_cache_index()
            self.next = crawler.load_matchdata('next')

            for season in self.avail['season'].values:
                self.selectFromYear.addItem(str(season), season)
                self.selectToYear.addItem(str(season), season)
            self.selectFromYear.currentIndexChanged.connect(self.show_start_days)
            self.selectToYear.currentIndexChanged.connect(self.show_end_days)


        def change_algo(self):
            self.selectHomeTeam.setEnabled(False)
            self.selectGuestTeam.setEnabled(False)
            self.predictButton.setEnabled(False)

        def show_start_days(self, index):
            self.reset_items(self.selectFromDay)
            season = self.selectFromYear.itemData(index)
            matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
            for day in range(1, matchdays + 1):
                self.selectFromDay.addItem(str(day), day)
            self.selectFromDay.setCurrentIndex(1)
            self.selectFromDay.setEnabled(True)

        def show_end_days(self, index):
            self.reset_items(self.selectToDay)
            season = self.selectToYear.itemData(index)
            matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
            for day in range(1, matchdays + 1):
                self.selectToDay.addItem(str(day), day)
            self.selectToDay.setCurrentIndex(matchdays)
            self.selectToDay.setEnabled(True)

        def reset_items(self, box):
            """Clears all but the first item from a given Combobox.

            Args:
                box (QComboBox): Combobox that will be cleared.
            """
            label = box.itemText(0)
            box.clear()
            box.addItem(label, None)
            box.model().item(0).setEnabled(False)

        def toggle_force_update(self, event):
            if event.type() == QtCore.QEvent.MouseButtonPress:
                state = self.forceUpdateBox.isChecked()
                self.forceUpdateBox.setChecked(not state)

        def crawlercall(self):
            """Gets the data between the chosen timeframe and filters it for the home team and guest team. Then it fills the combobox
            for the home team and guest team with the teams names.
            """
            self.crawlerButton.setEnabled(False)
            self.selectHomeTeam.setEnabled(False)
            self.selectGuestTeam.setEnabled(False)
            self.trainingButton.setEnabled(False)
            self.predictButton.setEnabled(False)
            self.reset_items(self.selectHomeTeam)
            self.reset_items(self.selectGuestTeam)
            fromSeason = self.selectFromYear.currentData()
            fromDay = self.selectFromDay.currentData()
            toSeason = self.selectToYear.currentData()
            toDay = self.selectToDay.currentData()
            forceUpdate = self.forceUpdateBox.isChecked()

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
            """
            """
            if self.selectAlgo.currentText() == 'Baseline Algorithm':
                self.model = BaselineAlgo(self.matchdata)
            elif self.selectAlgo.currentText() == 'Poisson Regression':
                self.model = PoissonRegression(self.matchdata)
            elif self.selectAlgo.currentText() == 'Dixon Coles Algorithm':
                self.model = DixonColes(self.matchdata)

            self.selectHomeTeam.setEnabled(True)
            self.selectGuestTeam.setEnabled(True)
            self.predictButton.setEnabled(True)
            self.statisticbutton.setEnabled(True)


        def resultscall(self):
            """
            """
            homeTeamID = self.selectHomeTeam.currentData()
            guestTeamID = self.selectGuestTeam.currentData()
            if None in (homeTeamID, guestTeamID):
                QMessageBox.warning(self, 'Invalid Teams', 'Please select a home and guest team.')
                return  # exit function
            elif homeTeamID == guestTeamID:
                QMessageBox.warning(self, 'Invalid Teams', 'Please select different home and guest teams.')
                return  # exit function

            self.homeIconCall()
            self.guestIconCall()
            homeTeamName = str(self.selectHomeTeam.currentText())
            guestTeamName = str(self.selectGuestTeam.currentText())
            predictionList = self.model.predict(homeTeamName, guestTeamName)
            self.resultLabel.setText("home: " + str(round(predictionList[0]*100,2)) + "%" + "   "
                                    + "draw: " + str(round(predictionList[1]*100,2)) + "%" + "   "
                                    + "guest: " + str(round(predictionList[2]*100,2)) + "%")

        # this will get called when you press the playday button.
        def playdaycall(self):
            # print(self.next['season'].to_string() + self.next['datetime'].to_string())
            output = self.next.to_string()
            list = self.next.to_dict('records')
            # print(list)
            # self.playdayLabel.setText(self.next['datetime'].to_string + self.next['homeTeamName'].to_string + self.next['guestTeamName'].to_string)
            self.playdayLabel.setText(self.next['season'].to_string(index=False)+"  " + self.next['datetime'].to_string(index=False)+"  " +
            self.next['homeTeamName'].to_string(index=False)+"   vs   " + self.next['guestTeamName'].to_string(index=False))
            print(output[1-200])

        # this will get called when you select the guest Team.
        def guestIconCall(self):
            """
            """
            guestIcon = self.teamdata.loc[self.teamdata['ID'] == self.selectGuestTeam.currentData(), 'icon'].values[0]
            guestIconPath = f'{crawler.g_cache_path}/guestIcon.png'
            urllib.request.urlretrieve(guestIcon, guestIconPath)
            pixmap = QtGui.QPixmap(guestIconPath)
            self.guestIcon.setPixmap(pixmap.scaled(100, 100))

            # this will get called when you select the home Team.
        def homeIconCall(self):
            """
            """
            homeIcon = self.teamdata.loc[self.teamdata['ID'] == self.selectHomeTeam.currentData(), 'icon'].values[0]
            homeIconPath = f'{crawler.g_cache_path}/homeIcon.png'
            urllib.request.urlretrieve(homeIcon, homeIconPath)
            pixmap = QtGui.QPixmap(homeIconPath)
            self.homeIcon.setPixmap(pixmap.scaled(100, 100))

        # this will get called when you press the Show statistics button.
        def statisticscall(self):
            """
            """
            data_analytics.main(self.matchdata, self.selectHomeTeam.currentText(), self.selectGuestTeam.currentText())

        def retranslateUi(self, Dialog):
            """Rename all the objects to the desired names.

            Args:
                Dialog (QDialog): Main window
            """
            _translate = QtCore.QCoreApplication.translate
            Dialog.setWindowTitle(_translate('FuBaKI', 'FuBaKI'))
            self.selectHomeTeam.setItemText(0, _translate('Dialog', '(Select Home Team)'))
            self.crawlerButton.setText(_translate('Dialog', 'Activate Crawler'))
            self.playdayButton.setText(_translate('Dialog', 'Show upcoming matches'))
            self.selectGuestTeam.setItemText(0, _translate('Dialog', '(Select Guest Team)'))
            self.selectFromYear.setItemText(0, _translate('Dialog', 'Season'))
            self.selectFromDay.setItemText(0, _translate('Dialog', 'Match Day'))
            self.selectToYear.setItemText(0, _translate('Dialog', 'Season'))
            self.selectToDay.setItemText(0, _translate('Dialog', 'Match Day'))
            self.forceUpdateLabel.setText(_translate('Dialog', 'force re-caching'))
            self.predictButton.setText(_translate('Dialog', 'Show results'))
            self.trainingButton.setText(_translate('Dialog', 'Start training'))
            self.statisticbutton.setText(_translate('Dialog','more statistics'))
            self.selectTeamsLabel.setText(_translate('Dialog', '<html><head/><body><p><span style=\' font-size:11pt;\'>Select the home team and the guest team:</span></p></body></html>'))
            self.selectStartTimeLabel.setText(_translate('Dialog', '<html><head/><body><p><span style=\' font-size:11pt;\'>Select the start year and day:</span></p></body></html>'))
            self.selectAlgoLabel.setText(_translate('Dialog', '<html><head/><body><p><span style=\' font-size:11pt;\'>Select the algorithm you want to use:</span></p></body></html>'))
            self.selectEndTimeLabel.setText(_translate('Dialog', '<html><head/><body><p><span style=\' font-size:11pt;\'>Select the end year and day:</span></p></body></html>'))
            self.resultLabel.setText(_translate('Dialog', '<html><head/><body><p><span style=\' font-size:11pt;\'>  </span></p><p><br/></p></body></html>'))
            self.colon.setText(_translate('Dialog', '<html><head/><body><p><span style=\' font-size:31pt;\'> : </span></p><p><br/></p></body></html>'))


    # create the window
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
