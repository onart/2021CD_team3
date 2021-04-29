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
from procs.stt import start_recognition, get_recognition, RecognitionManager
import procs.makeTree as makeTree

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
        self.funct1=keyboard.on_press_key(key='`', callback=self.setToggle)
        self.funct2=keyboard.on_press_key(key='Escape', callback=self.escape)

    def setToggle(self, dummy):
        keyboard.press('backspace')
        if self.isActiveWindow():
            self.lib.SetForegroundWindow(self.hIdeWnd)
            # 조작 모드 변경 
        else:
            self.activateWindow()
            # 조작 모드 변경
    
    def escape(self, dummy):
        self.close()

    def closeEvent(self, event):
        print('ggg')
        try:
            keyboard.unhook_key(self.funct1)
            keyboard.unhook_key(self.funct2)
        except KeyError:
            print('already closed')
        finally:
            event.accept()

class fn_dialog(QDialog):  #새로운 창 for new_window
    def __init__(self, content):
        super().__init__()
        self.setupUI()
        for i in range(len(content)):
            self.fn_lst.insertItem(i, content[i])
        self.select_fn = None

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle("Seleck Ur function")

        label1 = QLabel("Function lst")

        self.fn_lst = QListWidget()

        self.pushButton1 = QPushButton("Select")
        self.pushButton1.clicked.connect(self.pushButtonClicked)

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.fn_lst, 0, 1)
        layout.addWidget(self.pushButton1, 0, 2)

        self.setLayout(layout)

    def pushButtonClicked(self):
        self.select_fn = self.fn_lst.currentItem()
        self.close()

class MyApp(QMainWindow, form_class):

    def __init__(self):
        super().__init__()

        QtGui.QFontDatabase.addApplicationFont('./resources/TmoneyRoundWindRegular.ttf')
        self.setFont(QtGui.QFont('티머니 둥근바람 Regular', 10))

        self.window_1 = None    # Alt+tab-like
        self.window_2 = None    # peek

        self.hIdeWnd=0          # IDE Window Handle

        self.ctx=threading.Thread(target=makeTree.scanTH, daemon=True)

        self.setupUi(self)
        self.button_for_newtab.clicked.connect(self.peeker)
        self.NewWindow.clicked.connect(self.new_window)
        self.voice.clicked.connect(self.record)
        self.termButton.clicked.connect(self.close)
        self.open_File.clicked.connect(self.fileopen)
        self.help_button.clicked.connect(self.help)
        self.dialog = QDialog()

        # window shape/titlebar/stayontop flag
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # button qss
        self.textButtons=(
            self.NewWindow,
            self.termButton,
            self.help_button,
            )

        for bu in self.textButtons:
            bu.setStyleSheet('QPushButton:hover{ color: Red; } QPushButton{background-color: rgba(0,0,0,0); border-radius: 5px;}')
        self.recording=False

        self.voice.setStyleSheet('''
        background-image: url(./resources/recoff.png);
        background-position: center;
        background-repeat: no-repeat;
        color: White;
        border:0px;
        ''')

        self.funct1=keyboard.on_press_key(key='shift', callback=self.korOn)
        self.funct2=keyboard.on_release_key(key='shift', callback=self.korOff)

        # gradient
        self.backBrush=QtGui.QLinearGradient(0,0,0,400)
        self.backBrush.setColorAt(0.0, QtGui.QColor(255, 255, 160))
        self.backBrush.setColorAt(1.0, QtGui.QColor(240, 200, 120))
        self.foregroundColor = QtGui.QColor(240,240,240)
        self.borderRadius=15
        
        #layout = QVBoxLayout(self)
        #layout.setContentsMargins(0, 0, 0, 0)
        #layout.setSpacing(0)

        # drag
        self.draggable = True
        self.dragging_threshould = 5
        self.__mousePressPos = None
        self.__mouseMovePos = None
        self.language_change = False #shift 눌려 있으면 ON
        # active window
        threading.Thread(target=wind.currentWindow, args=[self],daemon=True).start()

        # stt recognition manager
        self.rec_manager = RecognitionManager()

    def korOn(self, dummy):
        if not self.recording:
            return
        self.language_change=True
        self.voice.setStyleSheet(
            '''
                        background-image: url(./resources/recon_kor.png);
                        background-repeat: no-repeat;
                        background-position: center;
                        font-family: 티머니 둥근바람 Regular;
                        color: White;
                        border:0px;
            '''
        )

    def korOff(self, dummy):
        if not self.recording:
            return
        self.language_change=False
        self.voice.setStyleSheet(
                '''
                    background-image: url(./resources/recon.png);
                    background-repeat: no-repeat;
                    background-position: center;
                    font-family: 티머니 둥근바람 Regular;
                    color: White;
                    border:0px;
                '''
            )

    def new_window(self):  #알탭처럼 새로운 자식 창 열어주는 함수
        dlg = fn_dialog(['1','2','3'])
        dlg.exec_()
        try:
            _fn = dlg.select_fn.text()
            print("Selected function is {}".format(_fn))
        except AttributeError:
            print("Selected Nothing.")
    
    def record(self): # 음성인식 함수
        self.recording = not(self.recording)
        if self.recording:
            # QMessageBox.about(self, "음성인식처리", "음성인식시작")
            self.voice.setStyleSheet('''
                    background-image: url(./resources/recon.png);
                    background-repeat: no-repeat;
                    background-position: center;
                    font-family: 티머니 둥근바람 Regular;
                    color: White;
                    border:0px;
                    ''')

            self.rec_manager.start()
            
        else:
            #QMessageBox.about(self, "음성인식처리", "음성인식종료")
            self.voice.setStyleSheet('''
        background-image: url(./resources/recoff.png);
        background-position: center;
        background-repeat: no-repeat;
        font-family: 티머니 둥근바람 Regular;
        color: White;
        border:0px;
        ''')
            self.language_change=False
            
            self.rec_manager.stop()

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
        # 여기에서 해결이 필요함
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

    def soundIn(self, word):
        if self.language_change:    # 일반 명령어
            pass
        else:   # peek or seek
            makeTree.scanNgc()
            sel1=makeTree.POOL.soundIn(word)
            # sel1 중 하나를 선택하는 대화상자 띄우고 결과 sel2에 저장
            if len(sel1)==0:
                QMessageBox.about(self, "오류", "결과를 찾을 수 없습니다.\n정확한 발음으로 다시 시도해 주세요.")
                return
            if len(sel1)==1:
                sel2=sel1[0]
            else:
                ch1=fn_dialog(sel1)
                ch1.exec_()
                try:
                    sel2=ch1.select_fn.text()
                except AttributeError:  # 선택하지 않음
                    return
            # 단 sel1의 결과가 1개라면 생략
            sel3=makeTree.POOL[sel2]
            if len(sel3[0])+len(sel3[1])+len(sel3[2])==1:
                if len(sel3[0])==1:
                    sel4=makeTree.functs[sel3[0][0]]
                    state='fu'
                elif len(sel3[1])==1:
                    sel4=makeTree.classes[sel3[1][0]]
                    state='cl'
                else:
                    sel4=sel3[2][0]
                    state='fi'
            else:   # 파일, 클래스, 함수 중 있는 선택지 보여줌
                pass
            # peek 모드인지 seek 모드인지에 따라 구분 처리

    def fileopen(self): #새로운 파일 선택
        option = QFileDialog.Option()
        option |= QFileDialog.ShowDirsOnly
        filename = QFileDialog.getExistingDirectory(self,"select Directory")
        if len(filename)>0:
            self.topDirectory.setText(filename)
            makeTree.TOPDIR=filename
            if not self.ctx.is_alive():
                self.ctx.start()

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

