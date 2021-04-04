# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("prototype.ui")[0]

class MyApp(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.NewWindow.clicked.connect(self.lstadd)
        self.voice.clicked.connect(self.record)
    def record(self): #음성인식 함수
        QMessageBox.about(self, "음성인식처리", "음성인식시작")
    def lstadd(self):
        self.fn_lst.insertItem(0, 'function 1')
        self.fn_lst.insertItem(1, 'function 2')




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyApp()
    myWindow.show()
    app.exec_()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

