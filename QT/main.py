# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys, os, threading
import ctypes
import keyboard
sys.path.append(os.path.abspath('..'))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5 import uic
import procs.wind as wind

form_class = uic.loadUiType("prototype.ui")[0]
child_class = uic.loadUiType("child.ui")[0]

class HelpWindow(QDialog):
    def __init__(self, parent):
        super(HelpWindow, self).__init__(parent)
        uic.loadUi("Help.ui", self)
        self.termButton.clicked.connect(self.close)
        self.show()


class PeekerWindow(QMainWindow):
    def __init__(self, f, h): # f: 파일 이름(절대 경로), h: 쓰던 IDE 핸들
        super().__init__()
        self.lib=ctypes.windll.LoadLibrary('user32.dll')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.hIdeWnd=h
        keyboard.on_press_key(key='`', callback=self.setToggle)

    def setToggle(self, dummy):
        keyboard.press('backspace')
        if self.isActiveWindow():
            self.lib.SetForegroundWindow(self.hIdeWnd)
            # 조작 모드 변경
        else:
            self.activateWindow()
            # 조작 모드 변경
    def closeEvent(self, event):
        print('ggg')
        keyboard.on_press_key(key='`', callback=lambda x: [])   # 확인된 문제: on_press_key 취소가 비정상적
        event.accept()

class MyApp(QMainWindow, form_class):

    def __init__(self):
        super().__init__()

        self.window_1 = None    # Alt+tab-like
        self.window_2 = None    # peek

        self.hIdeWnd=0          # IDE Window Handle

        self.setupUi(self)
        self.button_for_newtab.clicked.connect(self.peeker)
        self.NewWindow.clicked.connect(self.new_window)
        self.voice.clicked.connect(self.record)
        self.termButton.clicked.connect(self.close)
        self.open_File.clicked.connect(self.fileopen)
        self.help_button.clicked.connect(self.help)
        self.dialog = QDialog()
        self.dialog_for_new_window = QDialog()
        self.select_fn = None
        # window shape/titlebar/stayontop flag
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # button qss
        self.textButtons=(
            self.NewWindow,
            # self.voice
            self.termButton,
            )

        for bu in self.textButtons:
            bu.setStyleSheet('QPushButton:hover{background-color: white;} QPushButton{background-color: rgba(0,0,0,0); border-radius: 5px;}')
        self.recording=False

        # gradient
        self.backBrush=QtGui.QLinearGradient(0,0,0,400)
        self.backBrush.setColorAt(0.0, QtGui.QColor(240, 240, 240))
        self.backBrush.setColorAt(1.0, QtGui.QColor(200, 200, 200))
        self.foregroundColor = QtGui.QColor(240,240,240)
        self.borderRadius=15
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # drag
        self.draggable = True
        self.dragging_threshould = 5
        self.__mousePressPos = None
        self.__mouseMovePos = None

        # active window
        threading.Thread(target=wind.currentWindow, args=[self],daemon=True).start()

    def new_window(self):  #알탭처럼 새로운 자식 창 열어주는 함수
        # 버튼 추가
        btnDialog = QPushButton("OK", self.dialog_for_new_window)
        btnDialog.move(110, 140)
        btnDialog.clicked.connect(self.close_window)

        #함수들 박스
        fn_lst_wiget = QListWidget(self.dialog_for_new_window)
        fn_lst_wiget.move(110,20)
        fn_lst_wiget.insertItem(0, 'fn1')
        fn_lst_wiget.insertItem(1, 'fn2')
        fn_lst_wiget.insertItem(2, 'fn3')

        # QDialog 세팅
        self.dialog_for_new_window.setWindowTitle('Dialog')
        self.dialog_for_new_window.setWindowModality(Qt.ApplicationModal)
        self.dialog_for_new_window.resize(700, 500)
        self.dialog_for_new_window.move(self.voice.rect().topRight())
        self.dialog_for_new_window.show()



    def close_window(self):
        self.select_fn = self.dialog_for_new_window.fn_lst_widget.currentItem() #dialog 내에 있는 Qlistwidget에서 현재 선택된 아이템을 가져오기...(가져오는 방법 연구)
        self.dialog_for_new_window.close()
    
    def record(self): # 음성인식 함수
        self.recording = not(self.recording)
        self.voice.setText(str(self.recording))
        if self.recording:
            #QMessageBox.about(self, "음성인식처리", "음성인식시작")
            self.voice.setStyleSheet('''
        background-image: url(./resources/recon.png);
        background-repeat: no-repeat;
        background-position: center;
        border:0px;
        ''')
            pass
        else:
            #QMessageBox.about(self, "음성인식처리", "음성인식종료")
            self.voice.setStyleSheet('''
        background-image: url(./resources/recoff.png);
        background-position: center;
        background-repeat: no-repeat;
        border:0px;
        ''')
            pass
        
    def lstadd(self):
        self.fn_lst.insertItem(0, 'function 1')
        self.fn_lst.insertItem(1, 'function 2')

    def paintEvent(self, event):
        # get current window size
        s = self.size()
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setPen(self.foregroundColor)
        qp.setBrush(self.backBrush)
        qp.drawRoundedRect(0, 0, s.width(), s.height(),
                           self.borderRadius, self.borderRadius)
        qp.end()

    def mousePressEvent(self, event):
        if self.draggable and event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()                # global
            self.__mouseMovePos = event.globalPos() - self.pos()    # local
            print(self.__mousePressPos)
            
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.__mousePressPos is None:
            super().mouseMoveEvent(event)
            return
        if self.draggable and event.buttons() & QtCore.Qt.LeftButton:
            globalPos = event.globalPos()
            moved = globalPos - self.__mousePressPos
            if moved.manhattanLength() > self.dragging_threshould:
                # move when user drag window more than dragging_threshould
                diff = globalPos - self.__mouseMovePos
                self.move(diff)
                self.__mouseMovePos = globalPos - self.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            if event.button() == QtCore.Qt.LeftButton:
                moved = event.globalPos() - self.__mousePressPos
                if moved.manhattanLength() > self.dragging_threshould:
                    # do not call click event or so on
                    event.ignore()
                self.__mousePressPos = None
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        # close all children
        if self.window_1 is not None:
            self.window_1.close()
        if self.window_2 is not None:
            self.window_2.close()
        super().close()

    def peeker(self, f):   # 다른 코드 띄워놓는 것. f: 볼 파일
        if self.hIdeWnd==0:
            return
        elif self.window_2 == None:
            self.window_2 = PeekerWindow(f, self.hIdeWnd)
            self.window_2.show()

    def fileopen(self): #새로운 파일 선택
        option = QFileDialog.Option()
        option |= QFileDialog.ShowDirsOnly
        filename = QFileDialog.getExistingDirectory(self,"select Directory")

        

    def help(self):
        HelpWindow(self)

    """ 임시로 만들어 놓은 dialog 추가 코드 입니다
    def help_detail(self):
        # 닫기 버튼
        btnDialog = QPushButton("Close", self.dialog)
        btnDialog.move(83, 330)
        btnDialog.clicked.connect(self.dialog_close)

        self.dialog.setWindowTitle('Dialog')
        self.dialog.move(1300, 300) #dialog 시작위치
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.resize(250, 400)
        self.dialog.show()
    
    def dialog_close(self):
        self.dialog.close()
    """

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyApp()
    myWindow.show()
    app.exec_()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

