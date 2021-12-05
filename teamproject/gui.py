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
import json
from teamproject.models import BaselineAlgo
#from PyQt5 import QtWidgets
#from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys
    


#from teamproject.crawler import fetch_data

from PyQt5 import QtCore, QtGui, QtWidgets
import sys


f = open('teamproject/matches.json',)
data = json.load(f)
model = BaselineAlgo(data)
#f.close()
  

def main():
    """
    Creates and shows the main window.
    """

    f = open('teamproject/matches.json',)
    data = json.load(f)
    model = BaselineAlgo(data)
    
    
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
            
            # combobox for the home team
            self.comboBox = QtWidgets.QComboBox(Dialog)
            self.comboBox.setGeometry(QtCore.QRect(60, 80, 301, 61))
            self.comboBox.setObjectName("comboBox")
            
            #Loop through the json file and get all the home clubs, this doesn't account for duplicates yet. 
            for team in data:
                self.comboBox.addItem(team['homeClub'])
            
            #Combobox 2 for the guest team
            self.comboBox_2 = QtWidgets.QComboBox(Dialog)
            self.comboBox_2.setGeometry(QtCore.QRect(670, 80, 301, 61))
            self.comboBox_2.setObjectName("comboBox_2")
            
            #Loop through the json file and get all the guest clubs, this doesn't account for duplicates yet. 
            for team in data:
                self.comboBox_2.addItem(team['guestClub'])

            #Crawler Button
            self.pushButton = QtWidgets.QPushButton(Dialog)
            self.pushButton.setGeometry(QtCore.QRect(0, 680, 331, 101))
            self.pushButton.setObjectName("Activate Crawler")
            self.pushButton.clicked.connect(self.crawlercall)
            
        
            #Training button
            self.pushButton_2 = QtWidgets.QPushButton(Dialog)
            self.pushButton_2.setGeometry(QtCore.QRect(330, 680, 331, 101))
            self.pushButton_2.setObjectName("Start training")
            self.pushButton_2.clicked.connect(self.trainingcall)
            
            
            self.resultsbutton = QtWidgets.QPushButton(Dialog)
            self.resultsbutton.setGeometry(QtCore.QRect(660, 680, 331, 101))
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
            self.pushButton.setText("Crawler running")
        
        #this will get called when you press the Start training button
        def trainingcall(self):
            pass
            

        #this will get called when you press the Show results button, I think i will do a popup with the winner.
        def resultscall(self):
            #printing for test purposes
            print(self.comboBox.currentText())

            #predict the Winner out of the 2 teams chosen in the comboboxes
            winner = model.predict_winner(str(self.comboBox.currentText()), str(self.comboBox_2.currentText()))
            
            #Test
            print(winner)

            f.close()
            """
            If winner[0] (which is the home win percentage) is higher then the winner[2] (which is the guest winner percentage), 
            then display the home team in the button text. Else display the guest team. I will probably change this to 
            a popup window at some point.
            """
            if winner[0] > winner[2]:
                self.resultsbutton.setText(self.comboBox.currentText())
            else:
                self.resultsbutton.setText(self.comboBox_2.currentText())



            
        def retranslateUi(self, Dialog): # Rename all the objects to the desired names
            _translate = QtCore.QCoreApplication.translate
            Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
            self.comboBox.setItemText(0, _translate("Dialog", "Choose the home team"))
            self.pushButton.setText(_translate("Dialog", "Activate Crawler"))
            self.comboBox_2.setItemText(0, _translate("Dialog", "Choose the guest team"))
            self.resultsbutton.setText(_translate("Dialog", "Show results"))
            self.pushButton_2.setText(_translate("Dialog", "Start training"))

    #create the window
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
   
