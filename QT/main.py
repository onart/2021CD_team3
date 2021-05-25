# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys, os, threading, queue, pyautogui, time
from multiprocessing.managers import BaseManager
import ctypes
import keyboard
sys.path.append(os.path.abspath('..'))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5 import uic
import procs.wind as wind
from procs.stt import RecognitionManager
import procs.makeTree as makeTree
import procs.kComm as kComm
import html
from macro import *

form_class = uic.loadUiType("prototype.ui")[0]
child_class = uic.loadUiType("child.ui")[0]

MODES=['명령', '탐색', '보기']
USRLIB=ctypes.windll.LoadLibrary('user32.dll')

class HelpWindow(QDialog):
    def __init__(self, parent):
        super(HelpWindow, self).__init__(parent)
        uic.loadUi("Help.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
        self.termButton.clicked.connect(self.close)
        self.roundener=Roundener(self)
        self.show()

    def paintEvent(self, event):
        # get current window size
        self.roundener.paintEvent(event)

    def mousePressEvent(self, event):
        self.roundener.mousePressEvent(event)   
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.roundener.mouseMoveEvent(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.roundener.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)

class PeekerWindow(QDialog):
    def __init__(self, sel, parent):
        super().__init__()

        if len(sel) != 1:
            fname=sel[1]
            fname=makeTree.rel2abs[fname]
            sp=sel[2]
            rp=sel[3]
        else:
            fname=sel[0]
            fname=makeTree.rel2abs[fname]
            sp=(1,1)
            rp=(-1,-1)

        self.setupUI(fname)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.hIdeWnd=parent.hIdeWnd
        self.pIdeWnd=parent.pIdeWnd
        self.base=parent
        self.funct1=keyboard.on_press_key(key='num lock', callback=self.setToggle)
        # self.tid=threading.get_native_id()
        self.DISP_NO=20 # 한 번에 보여줄 줄수
        if (parent.y()+160+350) > QDesktopWidget().availableGeometry().height():
            self.move(parent.x()-175, parent.y()-400)
        else:
            self.move(parent.x()-175, parent.y()+160)

        try:
            f=open(fname, encoding='UTF-8')
            lines=f.readlines()
        except UnicodeDecodeError:
            f.close()
            f=open(fname, encoding='cp949')
            lines=f.readlines()
        f.close()
        self.content=lines[sp[0]-1:rp[0]]
        self.content[0]=self.content[0][sp[1]-1:]
        self.content[-1]=self.content[-1][:rp[1]]
        self.scr=0  # 스크롤, 가장 위 행 넘버
        self.lim=len(self.content)-self.DISP_NO

        self.printContent()
        self.roundener=Roundener(self)


    def setupUI(self, fname):
        layout = QtWidgets.QVBoxLayout(self)
        self.label=QtWidgets.QLabel('content', self)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        layout.addWidget(QtWidgets.QLabel(fname,self))
        layout.addWidget(self.label)
        layout.addWidget(QtWidgets.QLabel('Num Lock으로 IDE와 주목을 이동할 수 있습니다.', self))
        self.setMinimumWidth(600)
        self.setMinimumHeight(350)



    def setToggle(self, dummy):
        if USRLIB.GetForegroundWindow() != self.hIdeWnd:
            USRLIB.SetForegroundWindow(self.hIdeWnd)
        else:
            cp=self.pos()
            x, y=pyautogui.position()
            pyautogui.click(cp.x()+30, cp.y()+30)
            pyautogui.moveTo(x, y)
            #print(USRLIB.SetForegroundWindow(int(self.winId())))

    def closeEvent(self, event):
        try:
            keyboard.unhook_key(self.funct1)
        except KeyError:
            pass
        finally:
            self.base.sub2=None
            event.accept()

    def paintEvent(self, event):
        self.roundener.paintEvent(event)

    def mousePressEvent(self, event):
        self.roundener.mousePressEvent(event)   
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.roundener.mouseMoveEvent(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.roundener.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key()==QtCore.Qt.Key_Down:
            self.oneDown()
        elif event.key()==QtCore.Qt.Key_Up:
            self.oneUp()

    def oneUp(self):
        if self.scr > 0:
            self.scr -= 1
            self.printContent()

    def oneDown(self):
        if self.scr < self.lim:
            self.scr += 1
            self.printContent()

    def printContent(self):
        self.label.setText(''.join(self.content[self.scr:self.scr+self.DISP_NO]))

#html 사용을 위한 클래스
class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(HTMLDelegate, self).__init__(parent)
        self.doc = QtGui.QTextDocument(self)

    def paint(self, painter, option, index):
        painter.save()
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        self.doc.setHtml(options.text)
        options.text = ""
        style = QtWidgets.QApplication.style() if options.widget is None \
            else options.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.Text))
        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, options, None)
        if index.column() != 0:
            textRect.adjust(5, 0, 0, 0)
        constant = 4
        margin = (option.rect.height() - options.fontMetrics.height()) // 2
        margin = margin - constant
        textRect.setTop(textRect.top() + margin)

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(self.doc.idealWidth(), self.doc.size().height())

class fn_dialog(QDialog):  #새로운 창 for new_window
    def __init__(self, content):
        super().__init__()
        
        self.setupUI()
        delegate = HTMLDelegate(self.fn_lst)
        self.fn_lst.setItemDelegate(delegate)
        self.fn_lst.setRowCount(len(content[0]) + len(content[1]) + len(content[2]))
        self.fn_start  = 0
        self.class_start = self.fn_start + len(content[0])
        self.file_start = self.class_start + len(content[1])
        self.fn_lst.setHorizontalHeaderLabels(['유형', '이름', '파일', '스코프', '매개변수'])
        idx_for_listWidget = 0
        for id_type, type_line in enumerate(content):
            if(type_line):
                if(id_type == 0): # 함수의 경우  [이름, 파일, 시작, 끝, 스코프, 매개변수]
                    for each_fun in type_line:
                        self.fn_lst.setItem(idx_for_listWidget, 0, QTableWidgetItem('함수'))
                        idx_for_paramer = {1:0, 2:1, 3:4, 4:5}
                        for col_ in range(1,5):
                            self.fn_lst.setItem(idx_for_listWidget, col_,QTableWidgetItem('<span style="color:red">{}</span>'.format(each_fun[idx_for_paramer[col_]])) )
                        idx_for_listWidget += 1

                elif(id_type == 1): # 클래스의 경우 [이름 , 파일, 시작, 끝]
                    for each_class in type_line:
                        self.fn_lst.setItem(idx_for_listWidget, 0, QTableWidgetItem('클래스'))
                        for col_ in range(1,3):
                            self.fn_lst.setItem(idx_for_listWidget, col_,QTableWidgetItem('<span style="color:blue">{}</span>'.format(each_class[col_-1])) )
                        idx_for_listWidget += 1

                else: # 파일의 경우 [이름]
                    for each_file in type_line:
                        self.fn_lst.setItem(idx_for_listWidget, 0, QTableWidgetItem('파일'))
                        self.fn_lst.setItem(idx_for_listWidget, 1,QTableWidgetItem('<span style="color:green">{}</span>'.format(each_file[0])) )
                        idx_for_listWidget += 1


            else:
                pass

        self.select_fn = []
        self.roundener=Roundener(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #USRLIB.SetForegroundWindow(int(self.winId()))
        self.activateWindow()

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        label1 = QLabel("다수의 결과를 찾았습니다.")

        self.fn_lst = QTableWidget()
        self.fn_lst.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fn_lst.setSelectionMode(QAbstractItemView.SingleSelection)
        self.fn_lst.setHorizontalHeaderLabels(['유형', '이름', '파일', '스코프', '매개변수'])
        self.fn_lst.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fn_lst.setColumnCount(5)
        self.pushButton1 = QPushButton("Select")
        self.pushButton1.clicked.connect(self.pushButtonClicked)

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.fn_lst, 0, 1)
        layout.addWidget(self.pushButton1, 0, 2)

        self.setLayout(layout)

    def pushButtonClicked(self):
        row = self.fn_lst.currentRow()


        if(0<= row <self.class_start):
            self.select_fn = [0, row]

        elif(self.class_start <= row < self.file_start):
            self.select_fn = [1, row - self.class_start]

        else:
            self.select_fn = [2, row - self.file_start]

        self.close()

    def paintEvent(self, event):
        self.roundener.paintEvent(event)

    def mousePressEvent(self, event):
        self.roundener.mousePressEvent(event)   
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.roundener.mouseMoveEvent(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.roundener.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)

class v_dialog(QDialog):  # 음성 선택지
    def __init__(self, content):
        super().__init__()
        self.vlist=content
        self.setupUI()
        self.fn_lst.insertItems(len(content),content)
        self.select_fn = None
        self.roundener=Roundener(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.funct1=keyboard.on_press_key(key='up', callback=self.upDown)
        self.funct2=keyboard.on_press_key(key='down', callback=self.upDown)
        #self.funct3=keyboard.on_press_key(key='Escape', callback=self.escape)
        #USRLIB.SetForegroundWindow(int(self.winId()))
        self.activateWindow()
        
    def setupUI(self):
        self.setGeometry(1100, 200, 300, 120)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setMinimumWidth(400)
        self.move(qr.topLeft())

        label1 = QLabel("이걸 찾으시나요?")

        self.fn_lst = QListWidget()
        self.pushButton1 = QPushButton("선택")
        self.pushButton1.clicked.connect(self.pushButtonClicked)

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.fn_lst, 0, 1)
        layout.addWidget(self.pushButton1, 0, 2)

        self.setLayout(layout)

    def upDown(self, dummy):
        try:
            keyboard.unhook_key(self.funct1)
        except KeyError:
            pass
        try:
            keyboard.unhook_key(self.funct2)
        except KeyError:
            pass
        self.funct1=None
        self.funct2=None
        cp=self.pos()
        x, y=pyautogui.position()
        pyautogui.click(cp.x()+200, cp.y()+20)
        pyautogui.moveTo(x, y)

    def pushButtonClicked(self):
        self.select_fn = self.fn_lst.currentItem()
        self.close()

    def paintEvent(self, event):
        self.roundener.paintEvent(event)

    def mousePressEvent(self, event):
        self.roundener.mousePressEvent(event)   
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.roundener.mouseMoveEvent(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.roundener.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)
    
    '''def escape(self, dummy):
        self.close()'''

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        #keyboard.unhook_key(self.funct3)
        try:
            keyboard.unhook_key(self.funct2)
        except KeyError:
            pass
        try:
            keyboard.unhook_key(self.funct1)
        except KeyError:
            pass
        return super().closeEvent(a0)


class Roundener: # 상속 전용 클래스
    def __init__(self, window, brush=None, borderRadius=15):
        self.window=window
        self.window.setFont(QtGui.QFont('티머니 둥근바람 Regular', 10))
        self.window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        if brush==None:
            self.backBrush=QtGui.QLinearGradient(0,0,0,400)
            self.backBrush.setColorAt(0.0, QtGui.QColor(255, 255, 160))
            self.backBrush.setColorAt(1.0, QtGui.QColor(240, 200, 120))
            self.foregroundColor = QtGui.QColor(240,240,240)
            # drag
            self.draggable = True
            self.dragging_threshould = 5
            self.__mousePressPos = None
            self.__mouseMovePos = None
            self.borderRadius=borderRadius
        else:
            self.backBrush=brush

    def paintEvent(self, event):
        s=self.window.size()
        qp=QtGui.QPainter()
        qp.begin(self.window)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setBrush(self.backBrush)
        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.borderRadius, self.borderRadius)
        qp.end()
    
    def mousePressEvent(self, event):
        if self.draggable and event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()                # global
            self.__mouseMovePos = event.globalPos() - self.window.pos()    # local

    def mouseMoveEvent(self, event):
        if self.__mousePressPos is None:
            return
        if self.draggable and event.buttons() & QtCore.Qt.LeftButton:
            globalPos = event.globalPos()
            moved = globalPos - self.__mousePressPos
            if moved.manhattanLength() > self.dragging_threshould:
                # move when user drag window more than dragging_threshould
                diff = globalPos - self.__mouseMovePos
                self.window.move(diff)
                self.__mouseMovePos = globalPos - self.window.pos()
                return diff

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            if event.button() == QtCore.Qt.LeftButton:
                moved = event.globalPos() - self.__mousePressPos
                if moved.manhattanLength() > self.dragging_threshould:
                    # do not call click event or so on
                    event.ignore()
                self.__mousePressPos = None


class SoundSig(QObject):
    sin=QtCore.pyqtSignal()



class MyApp(QMainWindow, form_class):

    def __init__(self):
        super().__init__()

        self.base_h = 140
        self.extended_h = 300
        QtGui.QFontDatabase.addApplicationFont('./resources/TmoneyRoundWindRegular.ttf')

        self.sub1=None
        self.sub2=None

        self.blue=False


        self.sin = SoundSig()
        self.sin.sin.connect(self.soundIn)

        self.hIdeWnd=0          # IDE Window Handle
        self.pIdeWnd=0          # IDE Window Pid
        
        self.ctx=threading.Thread(target=makeTree.scanTH, daemon=True)
        # active window
        threading.Thread(target=wind.currentWindow, args=[self],daemon=True).start()
        
        self.roundener=Roundener(self)

        self.setupUi(self)

        self.voice.clicked.connect(self.record)
        self.termButton.clicked.connect(self.close)
        self.open_File.clicked.connect(self.fileopen)
        self.help_button.clicked.connect(self.help)
        self.macroButton.clicked.connect(self.macro)
        self.help_btn.clicked.connect(self.resizeWindow)
        self.help_flag = True
        self.dialog = QDialog()

        self.vMode=0            # 0: basic(명령 모드, 한국어 인식), 1: seek(탐색 모드, 영어 인식), 2: peek(보기 모드, 영어 인식)
        self.voice.setText('시작')  # 꺼진 상태

        self.kCommands={
            '명령': lambda _: self.setVmode(0),
            '탐색': lambda _: self.setVmode(1),
            '보기': lambda _: self.setVmode(2),
            }

        # window shape/titlebar/stayontop flag
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.open_File.setStyleSheet('''
        background-image: url(./resources/folder.png); background-position: center;
        background-repeat: no-repeat;
        background-position: center;
        ''')
        # button qss
        self.textButtons=(
            self.termButton,
            self.help_button,
            self.macroButton,
            self.help_btn
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

        self.language_change = False #shift 눌려 있으면 ON

        # stt recognition manager
        self.q=queue.Queue()
        self.rec_manager = RecognitionManager(self.q, self.sin)
        kComm.loadSet()

    def setVmode(self, m):
        self.vMode=m
        if self.blue:
            return
        self.voice.setText(MODES[m])
        if m==0:
            if not self.language_change:
                #self.rec_manager.change_to('kor')
                self.language_change=True
        elif self.language_change:
            self.language_change=False
            #self.rec_manager.change_to('eng')
            

    def korOn(self, dummy):
        if self.blue:
            return
        self.blue=True
        if not self.recording:
            return
        if not self.language_change:
            self.language_change=True
            #self.rec_manager.change_to('kor')
        self.voice.setText('명령')
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
        if self.vMode != 0:
            self.language_change=False
            self.voice.setText(MODES[self.vMode])
            #self.rec_manager.change_to('eng')
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
        self.blue=False
    
    def record(self): # 음성인식 함수
        self.recording = not(self.recording)
        if self.recording:
            self.voice.setStyleSheet('''
                    background-image: url(./resources/recon.png);
                    background-repeat: no-repeat;
                    background-position: center;
                    font-family: 티머니 둥근바람 Regular;
                    color: White;
                    border:0px;
                    ''')
            self.voice.setText(MODES[self.vMode])
            self.rec_manager.start()
            if self.vMode==0:
                self.language_change=True
                #self.rec_manager.change_to('kor')
            
        else:
            self.voice.setStyleSheet('''
        background-image: url(./resources/recoff.png);
        background-position: center;
        background-repeat: no-repeat;
        font-family: 티머니 둥근바람 Regular;
        color: White;
        border:0px;
        ''')
            self.language_change=False
            self.blue=False
            self.voice.setText('시작')
            self.rec_manager.stop()

    def paintEvent(self, event):
        self.roundener.paintEvent(event)

    def mousePressEvent(self, event):
        self.roundener.mousePressEvent(event)   
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        diff=self.roundener.mouseMoveEvent(event)
        if diff and not self.help_flag:
            monitor_y = QDesktopWidget().availableGeometry().height()
            if (self.y() + 225 + 350) > monitor_y:
                self.help_dialog.move(self.x(), self.y() - 400)
            else:
                self.help_dialog.move(self.x(), self.y() + 160)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.roundener.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        # close all children
        # 여기에서 해결이 필요함
        if self.sub1 is not None:
            self.sub1.close()
        if self.sub2 is not None:
            self.sub2.close()
        if not self.help_flag:
            self.help_dialog.close()
        keyboard.unhook_all()
        super().close()

    def soundIn(self):
        word=self.q.get()
        self.vLabel.setText(word)

        # 자식 window가 있는 시점에서는 명령 무시하도록 조치
        if self.sub1 != None:
            return
        if self.activeWindow.text() == 'others':
            if USRLIB.SetForegroundWindow(self.hIdeWnd)==0:
                QMessageBox.about(self, "오류", "IDE가 감지되지 않았습니다.")
                return
            else:
                time.sleep(0.1)
                kComm.ideUP(self.activeWindow.text())
        else:
            kComm.ideUP(self.activeWindow.text())

        if self.language_change:    # 한국어
            word2=kComm.matchK(word)
            self.vLabel.setText(word+'->'+word2)
            if word2 in self.kCommands:  # 모드 전환
                self.kCommands[word2](0)
                return
            elif word2 in kComm.builtInCommands:     # 일반 명령어
                guide=kComm.execute(word2)
                self.vLabel.setText(word2+guide)
            elif word2 in kComm.builtInCommands:
                kComm.execute(word2)
            else:   # 유사도
                QMessageBox.about(self, "오류", "해당 명령어가 없습니다.")
                return
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
                self.sub1=v_dialog(sel1)
                self.sub1.exec_()
                try:
                    sel2=self.sub1.select_fn.text()
                except AttributeError:  # 선택하지 않음
                    self.sub1=None
                    return
                finally:
                    self.sub1=None
            # 단 sel1의 결과가 1개라면 생략
            sel3=makeTree.POOL[sel2]
            if type(sel3[0]) is not list: # 결과 1개. len 6이면 함수, 4면 클래스, 1이면 파일
                sel4=sel3
            else:   # 파일, 클래스, 함수 중 있는 선택지 보여줌
                # 간혹 선택지 하나일 때 이 지점에 와서 오류가 발생하기도 함, 해결 필요
                self.sub1=fn_dialog(sel3)
                self.sub1.exec_()
                try:
                    sel4=self.sub1.select_fn
                    sel4=sel3[sel4[0]][sel4[1]]
                except IndexError:
                    self.sub1=None
                    return
                finally:
                    self.sub1=None
            if self.vMode==1:   # seek
                kComm.opn(sel4)
                pass
            elif self.vMode==2: # peek
                if self.sub2 != None:
                    self.sub2.close()
                self.sub2=PeekerWindow(sel4, self)
                self.sub2.show()

    def fileopen(self): #새로운 파일 선택
        option = QFileDialog.Option()
        option |= QFileDialog.ShowDirsOnly
        filename = QFileDialog.getExistingDirectory(self,"select Directory")
        if len(filename)>0:
            self.topDirectory.setText(filename)
            makeTree.setTop(filename)
            if not self.ctx.is_alive():
                self.ctx.start()

    def help(self):
        HelpWindow(self)

    def macro(self):
        MacroWindow(self)

    class ComList(QDialog):
        def __init__(self, cx, cy):
            super().__init__()
            self.setMinimumWidth(250)
            self.setMaximumSize(250,350)
            monitor_y=QDesktopWidget().availableGeometry().height()
            if (cy + 225 + 350) > monitor_y:
                self.move(cx, cy - 400)
            else:
                self.move(cx, cy + 160)
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
            self.roundener=Roundener(self)
            bic=list(kComm.builtInCommands)
            half=len(bic)//2
            col1='\n'.join(bic[:half])
            col2='\n'.join(bic[half:])
            layout = QtWidgets.QHBoxLayout(self)
            layout.addWidget(QtWidgets.QLabel(col1, self))
            layout.addWidget(QtWidgets.QLabel(col2, self))




        def paintEvent(self, a0):
            self.roundener.paintEvent(a0)

    def resizeWindow(self):
        if self.help_flag:
            self.help_btn.setText('↑')
            self.help_flag = False
            self.help_dialog = self.ComList(self.x(), self.y())
            self.help_dialog.setWindowTitle('Help word')
            self.help_dialog.setMaximumSize(250, 350)
            self.help_dialog.show()

        else:
            self.help_btn.setText('↓')
            self.help_flag = True
            self.help_dialog.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = MyApp()
    myWindow.show()
    app.exec_()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
