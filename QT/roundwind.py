'''
    window 모양
'''
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname('..'))))

from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import procs.wind as wind

def hex2QColor(c):
    """Convert Hex color to QColor"""
    r=int(c[0:2],16)
    g=int(c[2:4],16)
    b=int(c[4:6],16)
    return QtGui.QColor(r,g,b)

class RoundInvButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, text='button'):
        super(RoundInvButton, self).__init__(parent)
        self.setStyleSheet('QPushButton:hover{background-color: white;} QPushButton{background-color: rgba(0,0,0,0); border-radius: 5px;}')
        self.setText(text)

class RoundedWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(RoundedWindow, self).__init__(parent)

        # make the window frameless
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # fix size
        self.resize(200,300)
        self.setMinimumSize(QtCore.QSize(200, 300))
        self.setMaximumSize(QtCore.QSize(200, 300))
        self.setObjectName("mainwind")

        self.foregroundColor = hex2QColor("ffffff")
        self.borderRadius = 15
        self.draggable = True
        self.dragging_threshould = 5
        self.__mousePressPos = None
        self.__mouseMovePos = None

        # gradient
        self.backBrush=QtGui.QLinearGradient(0,0,0,400)
        self.backBrush.setColorAt(0.0, QtGui.QColor(240, 240, 240))
        self.backBrush.setColorAt(1.0, QtGui.QColor(200, 200, 200))
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.exitButton = RoundInvButton(self, text='종료하기')
        self.exitButton.clicked.connect(self.exitB)

        threading.Thread(target=wind.currentWindow).start()
        self.exitButton.setText(wind.cur)

    def exitB(self):
        QtGui.qApp.exit()
    
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
            
        super(RoundedWindow, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.draggable and event.buttons() & QtCore.Qt.LeftButton:
            globalPos = event.globalPos()
            moved = globalPos - self.__mousePressPos
            if moved.manhattanLength() > self.dragging_threshould:
                # move when user drag window more than dragging_threshould
                diff = globalPos - self.__mouseMovePos
                self.move(diff)
                self.__mouseMovePos = globalPos - self.pos()
        super(RoundedWindow, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            if event.button() == QtCore.Qt.LeftButton:
                moved = event.globalPos() - self.__mousePressPos
                if moved.manhattanLength() > self.dragging_threshould:
                    # do not call click event or so on
                    event.ignore()
                self.__mousePressPos = None
        super(RoundedWindow, self).mouseReleaseEvent(event)

        # close event
        if event.button() == QtCore.Qt.RightButton:
            QtGui.qApp.exit()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = RoundedWindow()
    main.show()
    sys.exit(app.exec_())
