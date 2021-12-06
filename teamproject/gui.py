"""
Add your GUI code here.


from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
Form, Window = uic.loadUiType("teamproject/dialog.ui")

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
window.show()
app.exec()
"""


from PyQt5 import QtCore, QtGui, QtWidgets
import sys

import json
from teamproject.models import BaselineAlgo
from teamproject.models import PoissonRegression
from teamproject.crawler import get_data



#open the json file with all the matches, then load this data into the BaselineAlgo
f = open('teamproject/matches.json',)
data = json.load(f)
model = BaselineAlgo(data)
#f.close()
  

def main():
    """
    Creates and shows the main window.
    """

    f = open('teamproject/matches.json',)
    hardloaddata = json.load(f)
    model = BaselineAlgo(hardloaddata)
    
    
    # Add code here to create and initialize window.
    class Ui_Dialog(object):
        def setupUi(self, Dialog):
            Dialog.setObjectName("Dialog")
            Dialog.resize(1055, 841) # Set the window size


            # create the ok and cancel buttons
            self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
            self.buttonBox.setGeometry(QtCore.QRect(700, 800, 341, 32))
            self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
            self.buttonBox.setObjectName("buttonBox")

            #SelectStartTime label
            self.SelectStartTimeLabel = QtWidgets.QLabel(Dialog)
            self.SelectStartTimeLabel.setGeometry(QtCore.QRect(30, 80, 371, 31))
            self.SelectStartTimeLabel.setObjectName("SelectStartTimeLabel")
            
            #SelectEndTime label
            self.SelectEndTimeLabel = QtWidgets.QLabel(Dialog)
            self.SelectEndTimeLabel.setGeometry(QtCore.QRect(450, 80, 371, 31))
            self.SelectEndTimeLabel.setObjectName("SelectEndTimeLabel")

            #The combobox for the start year
            self.StartYearcomboBox = QtWidgets.QComboBox(Dialog)
            self.StartYearcomboBox.setGeometry(QtCore.QRect(40, 150, 104, 87))
            self.StartYearcomboBox.setObjectName("StartYearcomboBox")
            
            #Put all the years between 2001 and 2020 into the combobox.
            for x in range(2002, 2020):
                self.StartYearcomboBox.addItem(str(x))

             #The combobox for the start day
            self.StartDaycomboBox = QtWidgets.QComboBox(Dialog)
            self.StartDaycomboBox.setGeometry(QtCore.QRect(160, 150, 104, 87))
            self.StartDaycomboBox.setObjectName("StartDaycomboBox")
            
            #A year has 365 days, so put 1-365 into the combobox
            for x in range(1,366):
                self.StartDaycomboBox.addItem(str(x))

            #The combobox for the end year
            self.EndYearcomboBox = QtWidgets.QComboBox(Dialog)
            self.EndYearcomboBox.setGeometry(QtCore.QRect(450, 150, 104, 87))
            self.EndYearcomboBox.setObjectName("EndYearcomboBox")
            
            #Put all the years between 2001 and 2020 into the combobox.
            for x in range(2002, 2020):
                self.EndYearcomboBox.addItem(str(x))

             #The combobox for the end day
            self.EndDaycomboBox = QtWidgets.QComboBox(Dialog)
            self.EndDaycomboBox.setGeometry(QtCore.QRect(570, 150, 104, 87))
            self.EndDaycomboBox.setObjectName("EndDaycomboBox")

            #A year has 365 days, so put 1-365 into the combobox
            for x in range(1,366):
                self.EndDaycomboBox.addItem(str(x))
            
             #Select the teams label
            self.SelectTeamLabel = QtWidgets.QLabel(Dialog)
            self.SelectTeamLabel.setGeometry(QtCore.QRect(30, 300, 371, 31))
            self.SelectTeamLabel.setObjectName("SelectTeamLabel")

            # homecomboBox for the home team
            self.homecomboBox = QtWidgets.QComboBox(Dialog)
            self.homecomboBox.setGeometry(QtCore.QRect(60, 380, 301, 61))
            self.homecomboBox.setObjectName("homecomboBox")
            
            #Loop through the json file and get all the home clubs, this doesn't account for duplicates yet. 
            for team in data:
                self.homecomboBox.addItem(team['homeClub'])
            
            #Guest Combobox for the guest team
            self.guestcomboBox = QtWidgets.QComboBox(Dialog)
            self.guestcomboBox.setGeometry(QtCore.QRect(570, 380, 301, 61))
            self.guestcomboBox.setObjectName("guestcomboBox")
            
            #Result label
            self.resultLabel = QtWidgets.QLabel(Dialog)
            self.resultLabel.setGeometry(QtCore.QRect(410, 680, 371, 31))
            self.resultLabel.setObjectName("resultLabel")

            #Crawler Button
            self.crawlerbutton = QtWidgets.QPushButton(Dialog)
            self.crawlerbutton.setGeometry(QtCore.QRect(0, 480, 331, 101))
            self.crawlerbutton.setObjectName("Activate Crawler")
            self.crawlerbutton.clicked.connect(self.crawlercall)
            
        
            #Training button
            self.trainingbutton = QtWidgets.QPushButton(Dialog)
            self.trainingbutton.setGeometry(QtCore.QRect(330, 480, 331, 101))
            self.trainingbutton.setObjectName("Start training")
            self.trainingbutton.clicked.connect(self.trainingcall)
            
            
            self.resultsbutton = QtWidgets.QPushButton(Dialog)
            self.resultsbutton.setGeometry(QtCore.QRect(660, 480, 331, 101))
            self.resultsbutton.setObjectName("Show results")
            self.resultsbutton.clicked.connect(self.resultscall)

            #call the retranslate
            self.retranslateUi(Dialog)
            
            #ok button
            self.buttonBox.accepted.connect(Dialog.accept)
            
            #cancel button
            self.buttonBox.rejected.connect(Dialog.reject)
            
            QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        #this will get called when you press the activate crawler button
        def crawlercall(self):
            self.crawlerbutton.setText("Crawler running")
            #textboxValue = self.textbox.text()
            data = get_data(int(self.StartYearcomboBox.currentText()),int(self.StartDaycomboBox.currentText()), int(self.EndYearcomboBox.currentText()),int(self.EndDaycomboBox.currentText()))
            print(data.index)

              #Loop through the json file and get all the guest clubs, this doesn't account for duplicates yet. 
            for team in data.index:
                self.guestcomboBox.addItem(data.team['guestClub'])

        
        #this will get called when you press the Start training button
        def trainingcall(self):
            pass
            

        #this will get called when you press the Show results button, I think i will do a popup with the winner.
        def resultscall(self):

            #printing for test purposes
            print(self.homecomboBox.currentText())

            #predict the Winner out of the 2 teams chosen in the comboboxes
            winner = model.predict_winner(str(self.homecomboBox.currentText()), str(self.guestcomboBox.currentText()))
            
            #Test
            print(winner)

            f.close()
            """
            If winner[0] (which is the home win percentage) is higher then the winner[2] (which is the guest winner percentage), 
            then display the home team in the button text. Else display the guest team. I will probably change this to 
            a popup window at some point.
            """
            if winner[0] > winner[2]:
                self.resultLabel.setText("Results: " + self.homecomboBox.currentText())
            else:
                self.resultLabel.setText("Results: " + self.guestcomboBox.currentText())



            
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
            self.SelectEndTimeLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Select the end year and day:</span></p></body></html>"))
            self.resultLabel.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:11pt;\">Results:</span></p><p><br/></p></body></html>"))


    #create the window
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
   
