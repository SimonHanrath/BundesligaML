from PyQt5 import QtCore, QtGui, QtWidgets
import sys


from teamproject.models import BaselineAlgo
from teamproject.models import PoissonRegression
from teamproject import crawler

import pandas as pd
import json



def main():
    """
    Creates and shows the main window.
    """

    # Add code here to create and initialize window.
    class Ui_Dialog(object):

        def setupUi(self, Dialog):
            """
            Define all the Ui Elements in this method.
            """
            Dialog.setObjectName("Dialog")
            Dialog.resize(1055, 841) # Set the window size


            # create the ok and cancel buttons
            self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
            self.buttonBox.setGeometry(QtCore.QRect(700, 800, 341, 32))
            self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
            self.buttonBox.setObjectName("buttonBox")

            #A label that tells you to select the start time, to change the text have a look at the retranslateUI funktion
            self.SelectStartTimeLabel = QtWidgets.QLabel(Dialog)
            self.SelectStartTimeLabel.setGeometry(QtCore.QRect(30, 80, 371, 31))
            self.SelectStartTimeLabel.setObjectName("SelectStartTimeLabel")

            #A label that tells you to select the end time, to change the text have a look at the retranslateUI funktion
            self.SelectEndTimeLabel = QtWidgets.QLabel(Dialog)
            self.SelectEndTimeLabel.setGeometry(QtCore.QRect(450, 80, 371, 31))
            self.SelectEndTimeLabel.setObjectName("SelectEndTimeLabel")

            #The combobox to select the start year, choose from 2001-2020
            self.StartYearcomboBox = QtWidgets.QComboBox(Dialog)
            self.StartYearcomboBox.setGeometry(QtCore.QRect(40, 150, 104, 87))
            self.StartYearcomboBox.setObjectName("StartYearcomboBox")

            #Put all the years between 2001 and 2020 into the combobox.
            for x in range(2002, 2020):
                self.StartYearcomboBox.addItem(str(x))

            #The combobox to select the start day, choose from 1-365
            self.StartDaycomboBox = QtWidgets.QComboBox(Dialog)
            self.StartDaycomboBox.setGeometry(QtCore.QRect(160, 150, 104, 87))
            self.StartDaycomboBox.setObjectName("StartDaycomboBox")

            #A year has 365 days, so put 1-365 into the combobox
            for x in range(0,366):
                self.StartDaycomboBox.addItem(str(x))

            #The combobox to select the end year, choose from 2001-2020
            self.EndYearcomboBox = QtWidgets.QComboBox(Dialog)
            self.EndYearcomboBox.setGeometry(QtCore.QRect(450, 150, 104, 87))
            self.EndYearcomboBox.setObjectName("EndYearcomboBox")

            #Put all the years between 2001 and 2020 into the combobox.
            for x in range(2002, 2020):
                self.EndYearcomboBox.addItem(str(x))

             #The combobox to select the end day, choose from 1-365
            self.EndDaycomboBox = QtWidgets.QComboBox(Dialog)
            self.EndDaycomboBox.setGeometry(QtCore.QRect(570, 150, 104, 87))
            self.EndDaycomboBox.setObjectName("EndDaycomboBox")

            #A year has 365 days, so put 1-365 into the combobox
            for x in range(0,366):
                self.EndDaycomboBox.addItem(str(x))


            #Activate crawler Button
            self.crawlerbutton = QtWidgets.QPushButton(Dialog)
            self.crawlerbutton.setGeometry(QtCore.QRect(50, 250, 331, 101))
            self.crawlerbutton.setObjectName("Activate Crawler")
            self.crawlerbutton.clicked.connect(self.crawlercall)

            #a label that tells you to select the team, to change the text have a look at the retranslateUI funktion
            self.SelectTeamLabel = QtWidgets.QLabel(Dialog)
            self.SelectTeamLabel.setGeometry(QtCore.QRect(30, 380, 371, 31))
            self.SelectTeamLabel.setObjectName("SelectTeamLabel")

            #the combobox to select the home team
            self.homecomboBox = QtWidgets.QComboBox(Dialog)
            self.homecomboBox.setGeometry(QtCore.QRect(60, 430, 301, 61))
            self.homecomboBox.setObjectName("homecomboBox")

            #the combobox to select the guest team
            self.guestcomboBox = QtWidgets.QComboBox(Dialog)
            self.guestcomboBox.setGeometry(QtCore.QRect(570, 430, 301, 61))
            self.guestcomboBox.setObjectName("guestcomboBox")

            #Select the Algo label, to change the text have a look at the retranslateUI funktion
            self.SelectAlgoLabel = QtWidgets.QLabel(Dialog)
            self.SelectAlgoLabel.setGeometry(QtCore.QRect(30, 510, 371, 31))
            self.SelectAlgoLabel.setObjectName("SelectAlgoLabel")

            #Algocombobox: Select the algorithm you want to use
            self.algocomboBox = QtWidgets.QComboBox(Dialog)
            self.algocomboBox.setGeometry(QtCore.QRect(60, 570, 301, 61))
            self.algocomboBox.setObjectName("algocomboBox")
            self.algocomboBox.addItem("Baseline Algorithm")
            self.algocomboBox.addItem("Poisson Regression Algorithm")

            #start training button
            self.trainingbutton = QtWidgets.QPushButton(Dialog)
            self.trainingbutton.setGeometry(QtCore.QRect(100, 660, 331, 101))
            self.trainingbutton.setObjectName("Start training")
            self.trainingbutton.clicked.connect(self.trainingcall)

            #show Result Button
            self.resultsbutton = QtWidgets.QPushButton(Dialog)
            self.resultsbutton.setGeometry(QtCore.QRect(430, 660, 331, 101))
            self.resultsbutton.setObjectName("Show results")
            self.resultsbutton.clicked.connect(self.resultscall)

            #This label will show the results
            self.resultLabel = QtWidgets.QLabel(Dialog)
            self.resultLabel.setGeometry(QtCore.QRect(410, 780, 371, 31))
            self.resultLabel.setObjectName("resultLabel")

            #call the retranslate
            self.retranslateUi(Dialog)

            #ok button
            self.buttonBox.accepted.connect(Dialog.accept)

            #cancel button
            self.buttonBox.rejected.connect(Dialog.reject)

            QtCore.QMetaObject.connectSlotsByName(Dialog)

        def filterdata(self):
            """Gets the data between the chosen timeframe and filters it for the home team and guest team. Then it fills the combobox
            for the home team and guest team with the teams names.

            Returns:
                The pandas dataframe for the chosen timeframe
            """
            # this uses the get_data function out of the crawler.py to get the data in the time you choose in the comboboxes
            data = crawler.get_data(int(self.StartYearcomboBox.currentText()),int(self.StartDaycomboBox.currentText()), int(self.EndYearcomboBox.currentText()),int(self.EndDaycomboBox.currentText()))
            teams = crawler.get_teams(data)
            self.homecomboBox.addItems(teams['name'])
            self.guestcomboBox.addItems(teams['name'])
            return data

        #this will get called when you press the activate crawler button
        def crawlercall(self):

            #change text of the crawler button
            self.crawlerbutton.setText("Crawler finished collecting data")

            #call the filterdata funktion to generate the data from the crawler
            self.filterdata()

        def trainAlgo(self):
            """predicts the winner with the models.py algorithms. doesn't work automaticly yet

             Returns:
                a string, homeName or guestName, depending on the winner
            """
            #depending on the text in the combobox, the algorithm is choosen
            if self.algocomboBox.currentText() == "Baseline Algorithm":
                model = BaselineAlgo(self.filterdata())
                print("Baseline Algorithm")

            elif self.algocomboBox.currentText() == "Poisson Regression Algorithm":
                model = PoissonRegression(self.filterdata())
                print("Poisson Regression Algorithm")

            predictionlist = model.predict(str(self.homecomboBox.currentText()), str(self.guestcomboBox.currentText()))

            """
            If predictionlist[0] (which is the home win percentage) is higher then the predictionlist[2] (which is the guest winner percentage),
            then set set the winner to "homeClub"
            """
            if predictionlist[0] > predictionlist[2]:
                winner = "homeClub"
            else:
                winner = "guestClub"

            return winner

        #this will get called when you press the Start training button
        def trainingcall(self):

            #train the algorithm and return the winner
            self.trainAlgo()
            #set the buttons text
            self.trainingbutton.setText("Training finished")

        #this will get called when you press the Show results button.
        def resultscall(self):

            winner = self.trainAlgo()

            #Set the Result label text to the winner
            if winner == "homeClub":
                self.resultLabel.setText("Results:  " + self.homecomboBox.currentText()+ " will win")

            else:
                self.resultLabel.setText("Results:  " + self.guestcomboBox.currentText()+ " will win")





        def retranslateUi(self, Dialog): # Rename all the objects to the desired names
            _translate = QtCore.QCoreApplication.translate
            Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
            self.homecomboBox.setItemText(0, _translate("Dialog", "Choose the home team"))
            self.crawlerbutton.setText(_translate("Dialog", "Activate Crawler"))
            self.guestcomboBox.setItemText(0, _translate("Dialog", "Choose the guest team"))
            self.StartYearcomboBox.setItemText(0, _translate("Dialog", "Start year"))
            self.StartDaycomboBox.setItemText(0, _translate("Dialog", "Start day"))
            self.EndYearcomboBox.setItemText(0, _translate("Dialog", "End year"))
            self.EndDaycomboBox.setItemText(0, _translate("Dialog", "End day"))
            self.resultsbutton.setText(_translate("Dialog", "Show results"))
            self.trainingbutton.setText(_translate("Dialog", "Start training"))
            self.SelectTeamLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the home team and the guest team:</span></p></body></html>"))
            self.SelectStartTimeLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the start year and day:</span></p></body></html>"))
            self.SelectAlgoLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the algorithm you want to use:</span></p></body></html>"))
            self.SelectEndTimeLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the end year and day:</span></p></body></html>"))
            self.resultLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Results:</span></p><p><br/></p></body></html>"))


    #create the window
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
