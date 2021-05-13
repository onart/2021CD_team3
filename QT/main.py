# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys, os, threading, queue
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

form_class = uic.loadUiType("prototype.ui")[0]
child_class = uic.loadUiType("child.ui")[0]

MODES=['명령', '탐색', '보기']
USRLIB=ctypes.windll.LoadLibrary('user32.dll')

class MacroWindow(QDialog):
    def __init__(self, parent):
        super(MacroWindow, self).__init__(parent)
        uic.loadUi("macro.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
        self.roundener=Roundener(self)

        self.setupUI()
        
        self.show()

    def setupUI(self):
        self.c = SaveSig()
        self.c.sig.connect(self.setTableAndShow)
        
        self.helpButton.clicked.connect(self.help)
        self.addButton.clicked.connect(self.add)
        self.closeButton.clicked.connect(self.close)

        self.tableWidget.doubleClicked.connect(self.addWithDoubleClick)
        self.setTableWidget()

    def setTableAndShow(self, tup):
        kComm.kCommands[tup[0]] = tup[1]
        print(kComm.kCommands)
        self.setTableWidget()
        self.show()

    def setTableWidget(self):
        self.tableWidget.setRowCount(len(kComm.kCommands.keys()))
        
        self.tableWidget.setColumnCount(2)
        self.table = []
        for i, key in enumerate(kComm.kCommands.keys()):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(key))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(len(kComm.kCommands[key]))))
            self.table.append(key)
        
        column_headers = ['이름', '구성 명령어 수']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        self.tableWidget.verticalHeader().setDefaultSectionSize(15)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        self.tableWidget.setColumnWidth(0, int(self.width()*5/10))
        
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

    def help(self):
        HelpWindow(self)

    def add(self):
        MacroAddWindow(self, self.c)
            

    def addWithDoubleClick(self):
        rows = []
        for idx in self.tableWidget.selectionModel().selectedIndexes():
            rows.append(idx.row())

        MacroAddWindow(self, self.c, self.table[rows[0]])
        

class MacroAddWindow(QDialog):
    def __init__(self, parent, cc, macroName=''):
        super(MacroAddWindow, self).__init__(parent)
        uic.loadUi("macroAdd.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
        self.roundener=Roundener(self)

        self.cc = cc
        self.setupUI(macroName)

        self.show()

    def setupUI(self, macroName):
        self.c = SaveSig()
        self.c.sig.connect(self.setTableAndShow)
        
        self.addButton.clicked.connect(self.add)
        self.removeButton.clicked.connect(self.remove)
        self.cancelButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.save)

        self.lineEdit.setText(macroName)
        if macroName != '':
            self.lineEdit.setReadOnly(True)

            # commands for test
            data = list(kComm.kCommands[macroName])
            self.setTableWidget(data)
            
        else:
            data = list()
            self.setTableWidget(data)

    def getTableData(self):
        print("in getTableData")
        data = []
        for row in range(self.tableWidget.rowCount()):
            name = self.tableWidget.item(row, 1).text()
            content = self.tableWidget.item(row, 2).text()
            data.append((name, content))

        print(data)

        return data
                

    def setTableAndShow(self, tup):
        data = self.getTableData()
        if tup[0]=='시간 지연':
            try:
                if tup[1]=='inf':
                    raise ValueError
                f=float(tup[1])
                if not f>0:
                    raise ValueError
            except ValueError:
                tup=('시간 지연', '0.02')
        data.append(tup)
        self.setTableWidget(data)
        self.show()

    def setTableWidget(self, data):
        self.tableWidget.setRowCount(len(data))
        
        self.tableWidget.setColumnCount(3)
        for i, tup in enumerate(data):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(tup[0]))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(tup[1]))
        
        column_headers = ['순번', '유형', '내용']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        self.tableWidget.verticalHeader().setDefaultSectionSize(15)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        self.tableWidget.setColumnWidth(0, 40)
        self.tableWidget.setColumnWidth(1, 70)

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

    def add(self):  
        # 여기에 '위치'까지 들어가도록(기준: 현재 선택된 행의 아래)
        # 현재 기존 값 수정하려고 더블클릭하면 이 창이 안 열리고 텍스트 수정만 가능한 거 수정 필요. 위의 addwithdoubleclick처럼
        MacroDetailWindow(self, self.c)

    def remove(self):
        rows = []
        for idx in self.tableWidget.selectionModel().selectedIndexes():
            rows.append(idx.row())

        if rows != []:
            data = self.getTableData()
            del data[rows[0]]
            self.setTableWidget(data)
            self.show()

    def save(self):
        name = self.lineEdit.text()
        # 명령은 한글 or 띄어쓰기로만 작성 가능한 것으로 고지
        name=' '.join(name.split())
        for ch in name:
            if ch == ' ':
                continue
            elif ch<'가' or ch>'힣':
                name=''
                QMessageBox.about(self,'이름 오류','한글만 입력 가능합니다.')
                break
        # 중복 불가능도 고지해야 함
        if name != '':
            data = self.getTableData()
            self.cc.sig.emit((name, data))
            self.close()


class SaveSig(QObject):
    sig=QtCore.pyqtSignal(object)


class MacroDetailWindow(QDialog):
    def __init__(self, parent, c):
        super(MacroDetailWindow, self).__init__(parent)
        uic.loadUi("macroDetail.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
        self.roundener=Roundener(self)

        self.c = c
        self.setupUI()

        self.show()

    def setupUI(self):
        self.cancelButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.save)

        self.comboBox.addItems(['명령', '팔레트', '시간 지연', '키 입력'])
        self.comboBox.currentTextChanged.connect(self.onTypeChange)

    def onTypeChange(self, event):
        if event=='키 입력':
            # 입력된 키 받아서 저장, 직접 수정 불가능, 디폴트값 ctrl
            self.lineEdit.setReadOnly(True)
            self.lineEdit.setText('ctrl')
            threading.Thread(target=self.readKey, daemon=True).start()
        else:
            # 자유 입력
            self.lineEdit.setReadOnly(False)
    
    def readKey(self):
        while self.comboBox.currentText()=='키 입력':
            k=keyboard.read_key()
            if self.comboBox.currentText()!='키 입력':
                break
            self.lineEdit.setText(k)

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

    def save(self):
        self.c.sig.emit((self.comboBox.currentText(), self.lineEdit.text()))
        self.close()
        

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

    def closeEvent(self, event):
        pass

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
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.hIdeWnd=parent.hIdeWnd
        self.base=parent
        self.funct1=keyboard.on_press_key(key='num lock', callback=self.setToggle)
        self.funct2=keyboard.on_press_key(key='Escape', callback=self.escape)

        self.DISP_NO=20 # 한 번에 보여줄 줄수

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
        layout = QtWidgets.QVBoxLayout()

        self.label=QtWidgets.QLabel('content', self)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        layout.addWidget(QtWidgets.QLabel(fname,self), 0)
        layout.addWidget(self.label, 1)

    def setToggle(self, dummy):
        if self.isActiveWindow():
            USRLIB.SetForegroundWindow(self.hIdeWnd)
        else:
            self.activateWindow()
    
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
            self.base.window_2=None
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

        self.fn_lst.setHorizontalHeaderLabels(['Item type', 'name', '들어가 있는 파일명', 'scope', 'parameter'])
        idx_for_listWidget = 0
        for id_type, type_line in enumerate(content):
            if(type_line):
                if(id_type == 0): # 함수의 경우  [이름, 파일, 시작, 끝, 스코프, 매개변수]
                    for each_fun in type_line:
                        self.fn_lst.setItem(idx_for_listWidget, 0, QTableWidgetItem('Function'))
                        idx_for_paramer = {1:0, 2:1, 3:4, 4:5}
                        for col_ in range(1,5):
                            self.fn_lst.setItem(idx_for_listWidget, col_,QTableWidgetItem('<span style="color:red">{}</span>'.format(each_fun[idx_for_paramer[col_]])) )
                        idx_for_listWidget += 1

                elif(id_type == 1): # 클래스의 경우 [이름 , 파일, 시작, 끝]
                    for each_class in type_line:
                        self.fn_lst.setItem(idx_for_listWidget, 0, QTableWidgetItem('Class'))
                        for col_ in range(1,3):
                            self.fn_lst.setItem(idx_for_listWidget, col_,QTableWidgetItem('<span style="color:blue">{}</span>'.format(each_class[col_-1])) )
                        idx_for_listWidget += 1

                else: # 파일의 경우 [이름]
                    for each_file in type_line:
                        self.fn_lst.setItem(idx_for_listWidget, 0, QTableWidgetItem('File'))
                        self.fn_lst.setItem(idx_for_listWidget, 1,QTableWidgetItem('<span style="color:green">{}</span>'.format(each_file[0])) )
                        idx_for_listWidget += 1


            else:
                pass

        self.select_fn = None
        self.roundener=Roundener(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        USRLIB.SetForegroundWindow(int(self.winId()))
        self.activateWindow()

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.move(qr.topLeft())

        self.setWindowTitle("Seleck Ur function")

        label1 = QLabel("Select Item<br>You want<br>Function : Red<br>Class : Blue<br>File : Green")

        self.fn_lst = QTableWidget()
        self.fn_lst.setHorizontalHeaderLabels(['Item type', 'name', '들어가 있는 파일명', 'scope', 'parameter'])
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
        self.select_fn = self.fn_lst.takeItem(row, 1)
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
        USRLIB.SetForegroundWindow(int(self.winId()))
        self.activateWindow()

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        qr=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setMinimumWidth(400)
        self.move(qr.topLeft())

        label1 = QLabel("이걸 찾으시나요?")

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
            print(self.__mousePressPos)

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

        QtGui.QFontDatabase.addApplicationFont('./resources/TmoneyRoundWindRegular.ttf')

        self.window_1 = None    # Alt+tab-like
        self.window_2 = None    # peek
        self.sub1=None
        self.sub2=None

        self.sin = SoundSig()
        self.sin.sin.connect(self.soundIn)

        self.hIdeWnd=0          # IDE Window Handle

        self.ctx=threading.Thread(target=makeTree.scanTH, daemon=True)
        # active window
        threading.Thread(target=wind.currentWindow, args=[self],daemon=True).start()
        
        self.roundener=Roundener(self)

        self.setupUi(self)
        self.button_for_newtab.clicked.connect(self.peeker)
        self.NewWindow.clicked.connect(self.new_window)
        self.voice.clicked.connect(self.record)
        self.termButton.clicked.connect(self.close)
        self.open_File.clicked.connect(self.fileopen)
        self.help_button.clicked.connect(self.help)
        self.macroButton.clicked.connect(self.macro)
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
            self.NewWindow,
            self.termButton,
            self.help_button,
            self.macroButton
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

    def setVmode(self, m):
        print('mode:',m)
        self.vMode=m
        self.voice.setText(MODES[m])
        if m==0:
            if not self.language_change:
                self.rec_manager.change_to('kor')
                self.language_change=True
        elif self.language_change:
            self.language_change=False
            self.rec_manager.change_to('eng')
            

    def korOn(self, dummy):
        if not self.recording:
            return
        if not self.language_change:
            self.language_change=True
            self.rec_manager.change_to('kor')
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
            print(self.vMode)
            self.language_change=False
            self.voice.setText(MODES[self.vMode])
            self.rec_manager.change_to('eng')
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
        dlg = fn_dialog([[['aBc', 'main.py', (8, 12), (10, 9),'test1','self, dong'], ['ABc', 'test.py', (8, 12), (10, 9),'class1.fun2','self']], [['aBc', 'main.py', (8, 12), (10, 9)], ['aBC', 'wind.py', (8, 12), (10, 9)]], ['abc.py', 'abe.cpp']]) # just example , 나중에 여기에 함수랑 클래스 파일 이름 겹치는 것 들어올 것..
        dlg.exec_()
        try:
            _fn = dlg.select_fn.text()
            print("Selected function is {}".format(_fn))
        except AttributeError:
            print("Selected Nothing.")
    
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
                self.rec_manager.change_to('kor')
            
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
            self.voice.setText('시작')
            self.rec_manager.stop()

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

    def closeEvent(self, event):
        # close all children
        # 여기에서 해결이 필요함
        if self.window_1 is not None:
            self.window_1.close()
        if self.window_2 is not None:
            self.window_2.close()
        keyboard.unhook_all()
        super().close()

    def peeker(self, f):   # 다른 코드 띄워놓는 것. f: 볼 파일
        if self.hIdeWnd==0:
            return
        else:
            self.window_2 = PeekerWindow(('QT\\main.py',),self)
            self.window_2.show()

    def soundIn(self):
        word=self.q.get()
        if self.activeWindow.text() == 'others':
            if USRLIB.SetForegroundWindow(self.hIdeWnd)==0:
                QMessageBox.about(self, "오류1", "IDE가 감지되지 않았습니다.")
                print('IDE 없음')
                return

        # 자식 window가 있는 시점에서는 명령 무시하도록 조치
        if self.sub1 != None:
            return

        if self.language_change:    # 한국어
            if word in self.kCommands:  # 모드 전환
                self.kCommands[word](0)
                return
            elif True:                  # 일반 명령어
                kComm.execute(word)
                pass
            else:   # 유사도
                QMessageBox.about(self, "임시 오류", "해당 명령어가 없습니다.")
                return
        else:   # peek or seek
            makeTree.scanNgc()
            sel1=makeTree.POOL.soundIn(word)
            # sel1 중 하나를 선택하는 대화상자 띄우고 결과 sel2에 저장
            if len(sel1)==0:
                QMessageBox.about(self, "오류2", "결과를 찾을 수 없습니다.\n정확한 발음으로 다시 시도해 주세요.")
                return
            if len(sel1)==1:
                sel2=sel1[0]
            else:
                self.sub1=v_dialog(sel1)
                self.sub1.exec_()
                try:
                    sel2=self.sub1.select_fn.text()
                    print(sel2)
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
                self.sub1=fn_dialog(sel3)
                self.sub1.exec_()
                try:
                    sel4=self.sub1.select_fn.text() # text 말고 sel3의 성분으로 해야 함
                except AttributeError:
                    self.sub1=None
                    return
                finally:
                    self.sub1=None
            if self.vMode==1:   # seek
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

