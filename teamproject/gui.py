import sys
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QCheckBox, QApplication, QWidget, QMessageBox, QDialog, QComboBox
from teamproject import crawler
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
            """
            Dialog.setMinimumSize(1055, 841)
            Dialog.resize(1055, 841)

            # create the ok and cancel buttons
            self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
            self.buttonBox.setGeometry(QtCore.QRect(700, 800, 341, 32))
            self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
            self.buttonBox.setObjectName("buttonBox")

            # A label that tells you to select the start time, to change the text have a look at the retranslateUI funktion
            self.SelectStartTimeLabel = QtWidgets.QLabel(Dialog)
            self.SelectStartTimeLabel.setGeometry(QtCore.QRect(30, 80, 371, 31))
            self.SelectStartTimeLabel.setObjectName("SelectStartTimeLabel")

            # A label that tells you to select the end time, to change the text have a look at the retranslateUI funktion
            self.SelectEndTimeLabel = QtWidgets.QLabel(Dialog)
            self.SelectEndTimeLabel.setGeometry(QtCore.QRect(450, 80, 371, 31))
            self.SelectEndTimeLabel.setObjectName("SelectEndTimeLabel")

            # The combobox to select the start season
            self.StartYearcomboBox = QtWidgets.QComboBox(Dialog)
            self.StartYearcomboBox.setGeometry(QtCore.QRect(40, 150, 104, 87))
            self.StartYearcomboBox.setObjectName("StartYearcomboBox")
            self.StartYearcomboBox.addItem("SelectStartSeasonLabel")
            self.reset_items(self.StartYearcomboBox)

            # The combobox to select the start match day
            self.StartDaycomboBox = QtWidgets.QComboBox(Dialog)
            self.StartDaycomboBox.setGeometry(QtCore.QRect(160, 150, 104, 87))
            self.StartDaycomboBox.setObjectName("StartDaycomboBox")
            self.StartDaycomboBox.setEnabled(False)
            self.StartDaycomboBox.addItem("SelectStartMatchdayLabel")
            self.reset_items(self.StartDaycomboBox)

            # The combobox to select the end season
            self.EndYearcomboBox = QtWidgets.QComboBox(Dialog)
            self.EndYearcomboBox.setGeometry(QtCore.QRect(450, 150, 104, 87))
            self.EndYearcomboBox.setObjectName("EndYearcomboBox")
            self.EndYearcomboBox.addItem("SelectEndSeasonLabel")
            self.reset_items(self.EndYearcomboBox)

            # The combobox to select the end match day
            self.EndDaycomboBox = QtWidgets.QComboBox(Dialog)
            self.EndDaycomboBox.setGeometry(QtCore.QRect(570, 150, 104, 87))
            self.EndDaycomboBox.setObjectName("EndDaycomboBox")
            self.EndDaycomboBox.setEnabled(False)
            self.EndDaycomboBox.addItem("SelectEndMatchdayLabel")
            self.reset_items(self.EndDaycomboBox)

            # force update flag
            self.forceUpdateBox = QtWidgets.QCheckBox(Dialog)
            self.forceUpdateBox.setGeometry(QtCore.QRect(40, 210, 30, 30))
            self.forceUpdateLabel = QtWidgets.QLabel(Dialog)
            self.forceUpdateLabel.setGeometry(QtCore.QRect(60, 210, 100, 31))
            self.forceUpdateLabel.setObjectName("forceUpdateLabel")

            # activate crawler Button
            self.crawlerbutton = QtWidgets.QPushButton(Dialog)
            self.crawlerbutton.setGeometry(QtCore.QRect(50, 250, 331, 101))
            self.crawlerbutton.setObjectName("Activate Crawler")
            self.crawlerbutton.clicked.connect(self.crawlercall)

            # a label that tells you to select the team, to change the text have a look at the retranslateUI funktion
            self.SelectTeamLabel = QtWidgets.QLabel(Dialog)
            self.SelectTeamLabel.setGeometry(QtCore.QRect(30, 380, 371, 31))
            self.SelectTeamLabel.setObjectName("SelectTeamLabel")

            # the combobox to select the home team
            self.homecomboBox = QtWidgets.QComboBox(Dialog)
            self.homecomboBox.setGeometry(QtCore.QRect(60, 430, 301, 61))
            self.homecomboBox.setObjectName("homecomboBox")
            self.homecomboBox.setEnabled(False)
            self.homecomboBox.addItem("SelectHomeTeamLabel")
            self.reset_items(self.homecomboBox)

            # the combobox to select the guest team
            self.guestcomboBox = QtWidgets.QComboBox(Dialog)
            self.guestcomboBox.setGeometry(QtCore.QRect(570, 430, 301, 61))
            self.guestcomboBox.setObjectName("guestcomboBox")
            self.guestcomboBox.setEnabled(False)
            self.guestcomboBox.addItem("SelectGuestTeamLabel")
            self.reset_items(self.guestcomboBox)

            # select the Algo label, to change the text have a look at the retranslateUI funktion
            self.SelectAlgoLabel = QtWidgets.QLabel(Dialog)
            self.SelectAlgoLabel.setGeometry(QtCore.QRect(30, 510, 371, 31))
            self.SelectAlgoLabel.setObjectName("SelectAlgoLabel")

            # Algocombobox: Select the algorithm you want to use
            self.algocomboBox = QtWidgets.QComboBox(Dialog)
            self.algocomboBox.setGeometry(QtCore.QRect(60, 570, 301, 61))
            self.algocomboBox.setObjectName("algocomboBox")
            self.algocomboBox.addItem("Baseline Algorithm")
            self.algocomboBox.addItem("Poisson Regression Algorithm")
            self.algocomboBox.setEnabled(False)

            # start training button
            self.trainingbutton = QtWidgets.QPushButton(Dialog)
            self.trainingbutton.setGeometry(QtCore.QRect(100, 660, 331, 101))
            self.trainingbutton.setObjectName("Start training")
            self.trainingbutton.clicked.connect(self.trainingcall)
            self.trainingbutton.setEnabled(False)

            # show result button
            self.resultsbutton = QtWidgets.QPushButton(Dialog)
            self.resultsbutton.setGeometry(QtCore.QRect(430, 660, 331, 101))
            self.resultsbutton.setObjectName("Show results")
            self.resultsbutton.clicked.connect(self.resultscall)
            self.resultsbutton.setEnabled(False)

            # this label will show the results
            self.resultLabel = QtWidgets.QLabel(Dialog)
            self.resultLabel.setGeometry(QtCore.QRect(410, 780, 371, 31))
            self.resultLabel.setObjectName("resultLabel")

            # call the retranslate
            self.retranslateUi(Dialog)

            # ok button
            self.buttonBox.accepted.connect(Dialog.accept)

            # cancel button
            self.buttonBox.rejected.connect(Dialog.reject)

            QtCore.QMetaObject.connectSlotsByName(Dialog)

            # load available data
            crawler.refresh_cache()
            self.avail = crawler.load_cache_index()
            self.next = crawler.load_matchdata('next')
            seasonList = self.avail[['season', 'availMatchdays']].to_dict('records')
            for season in seasonList:
                year = season['season']
                matchdays = season['availMatchdays']
                self.StartYearcomboBox.addItem(str(year), year)
                self.EndYearcomboBox.addItem(str(year), year)
            self.StartYearcomboBox.currentIndexChanged.connect(self.show_start_days)
            self.EndYearcomboBox.currentIndexChanged.connect(self.show_end_days)

        def show_start_days(self, index):
            self.reset_items(self.StartDaycomboBox)
            season = self.StartYearcomboBox.itemData(index)
            matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
            for day in range(1, matchdays + 1):
                self.StartDaycomboBox.addItem(str(day), day)
            self.StartDaycomboBox.setCurrentIndex(1)
            self.StartDaycomboBox.setEnabled(True)

        def show_end_days(self, index):
            self.reset_items(self.EndDaycomboBox)
            season = self.EndYearcomboBox.itemData(index)
            matchdays = self.avail.loc[self.avail['season'] == season, 'availMatchdays'].values[0]
            for day in range(1, matchdays + 1):
                self.EndDaycomboBox.addItem(str(day), day)
            self.EndDaycomboBox.setCurrentIndex(matchdays)
            self.EndDaycomboBox.setEnabled(True)

        def reset_items(self, box):
            """
            """
            label = box.itemText(0)
            box.clear()
            box.addItem(label, None)
            box.model().item(0).setEnabled(False)

        def crawlercall(self):
            """Gets the data between the chosen timeframe and filters it for the home team and guest team. Then it fills the combobox
            for the home team and guest team with the teams names.
            """
            self.crawlerbutton.setEnabled(False)
            self.homecomboBox.setEnabled(False)
            self.guestcomboBox.setEnabled(False)
            self.algocomboBox.setEnabled(False)
            self.trainingbutton.setEnabled(False)
            self.resultsbutton.setEnabled(False)
            self.reset_items(self.homecomboBox)
            self.reset_items(self.guestcomboBox)
            fromSeason = self.StartYearcomboBox.currentData()
            fromDay = self.StartDaycomboBox.currentData()
            toSeason = self.EndYearcomboBox.currentData()
            toDay = self.EndDaycomboBox.currentData()
            forceUpdate = self.forceUpdateBox.isChecked()
            if None in (fromSeason, fromDay, toSeason, toDay):
                message = 'Selected interval incomplete.'
                QMessageBox.warning(self, 'Invalid interval', message)
            elif (fromSeason == toSeason and fromDay > toDay) or (fromSeason > toSeason):
                message = 'Please select a valid time interval.'
                QMessageBox.warning(self, 'Invalid interval', message)
            else:
                self.matchdata = crawler.get_data(
                    fromSeason, fromDay, toSeason, toDay, forceUpdate)
                self.teamdata = crawler.get_teams(self.matchdata)
                teamList = self.teamdata.to_dict('records')
                for team in teamList:
                    self.homecomboBox.addItem(team['name'], team['ID'])
                    self.guestcomboBox.addItem(team['name'], team['ID'])
                self.homecomboBox.setEnabled(True)
                self.guestcomboBox.setEnabled(True)
                self.algocomboBox.setEnabled(True)
                self.trainingbutton.setEnabled(True)
            self.crawlerbutton.setEnabled(True)

        def trainAlgo(self):
            """predicts the winner with the models.py algorithms. doesn't work automaticly yet

             Returns:
                a string, homeName or guestName, depending on the winner
            """
            homeTeamID = self.homecomboBox.currentData()
            guestTeamID = self.guestcomboBox.currentData()
            print(f'home: {homeTeamID}, guest: {guestTeamID}')
            if None in (homeTeamID, guestTeamID):
                QMessageBox.warning(self, 'Invalid Teams', 'Please select a guest and home team.')
                return # exit function

            # depending on the text in the combobox, the algorithm is choosen
            if self.algocomboBox.currentText() == "Baseline Algorithm":
                model = BaselineAlgo(self.matchdata)
                print("Baseline Algorithm")

            elif self.algocomboBox.currentText() == "Poisson Regression Algorithm":
                model = PoissonRegression(self.matchdata)
                print("Poisson Regression Algorithm")
            homeName = str(self.homecomboBox.currentText())
            guestName = str(self.guestcomboBox.currentText())
            predictionlist = model.predict(homeName, guestName)
            self.resultsbutton.setEnabled(True)

            """
            If predictionlist[0] (which is the home win percentage) is higher then the predictionlist[2] (which is the guest winner percentage),
            then set set the winner to "homeClub"
            """
            if predictionlist[0] > predictionlist[2]:
                winner = "homeClub"
            else:
                winner = "guestClub"

            return winner

        # this will get called when you press the Start training button
        def trainingcall(self):
            """
            """
            # train the algorithm and return the winner
            self.trainAlgo()
            # set the buttons text
            self.trainingbutton.setText("Training finished")

        # this will get called when you press the Show results button.
        def resultscall(self):
            """
            """
            winner = self.trainAlgo()
            # set the result label text to the winner
            if winner == "homeClub":
                self.resultLabel.setText("Results:  " + self.homecomboBox.currentText() + " will win")
            else:
                self.resultLabel.setText("Results:  " + self.guestcomboBox.currentText() + " will win")

        def retranslateUi(self, Dialog):
            """Rename all the objects to the desired names.
            """
            _translate = QtCore.QCoreApplication.translate
            Dialog.setWindowTitle(_translate("FuBaKI", "FuBaKI"))
            self.homecomboBox.setItemText(0, _translate("Dialog", "(Select Home Team)"))
            self.crawlerbutton.setText(_translate("Dialog", "Activate Crawler"))
            self.guestcomboBox.setItemText(0, _translate("Dialog", "(Select Guest Team)"))
            self.StartYearcomboBox.setItemText(0, _translate("Dialog", "Season"))
            self.StartDaycomboBox.setItemText(0, _translate("Dialog", "Match Day"))
            self.EndYearcomboBox.setItemText(0, _translate("Dialog", "Season"))
            self.EndDaycomboBox.setItemText(0, _translate("Dialog", "Match Day"))
            self.forceUpdateLabel.setText(_translate("Dialog", "force re-caching"))
            self.resultsbutton.setText(_translate("Dialog", "Show results"))
            self.trainingbutton.setText(_translate("Dialog", "Start training"))
            self.SelectTeamLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the home team and the guest team:</span></p></body></html>"))
            self.SelectStartTimeLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the start year and day:</span></p></body></html>"))
            self.SelectAlgoLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the algorithm you want to use:</span></p></body></html>"))
            self.SelectEndTimeLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the end year and day:</span></p></body></html>"))
            self.resultLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Results:</span></p><p><br/></p></body></html>"))

    # create the window
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
