from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5 import uic

from main import Roundener
import procs.kComm as kComm


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
        # 중복 불가능도 고지해야 함 (빌트인이랑도)
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
