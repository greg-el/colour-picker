import ctypes
import sys
import time
from os import getenv

import pyperclip
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QLayout, QPushButton, QSizePolicy, QWidget)
from Xlib import X, display

coord = ctypes.CDLL('./obj/coords.so')
coord.coordinates.restype = ctypes.c_int * 2

color = ctypes.CDLL('./obj/color.so')
color.makeHex.restype = ctypes.c_ulong
color.makeHex.argtypes = [ctypes.c_int, ctypes.c_int]

class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.addColorButton = QPushButton("+", self)
        self.num_buttons = 0
        self.window_pos_x = 0
        self.window_pos_y = 0
        self.initUI()

        
    def initUI(self):
        self.setWindowTitle("Pallet")
        self.setAttribute(Qt.WA_TranslucentBackground);
        self.addColorButton.clicked.connect(self.addButton)
        self.addColorButton.setStyleSheet("border-radius: 3px; height:40px; width:60px; background-color: #FFFFF6;")
        self.addColorButton.show()
        self.setGeometry(50, 50, 60, 40)
        self.show()
        

    def moveEvent(self, e):
        self.x = self.pos().x()
        self.y = self.pos().y()
        super(UI, self).moveEvent(e)

    @pyqtSlot()
    def addButton(self):
        color = getClickColor()
        button = QPushButton("#"+color, self)
        if self.num_buttons < 8:
            buttonX = self.num_buttons*60 
            buttonY = 0

            addColorButtonX = 60+self.num_buttons*60
            addColorButtonY = 0

            windowHeight = 40
            windowWidth = 60+buttonX+60
        elif self.num_buttons >= 8:
            buttonX = (self.num_buttons-8)*60
            buttonY = 80

            addColorButtonX = 60+(self.num_buttons-8)*60
            addColorButtonY = 80

            windowHeight = 80
            windowWidth = 480+60
        
        self.addColorButton.move(addColorButtonX, 0)
        self.setGeometry(self.x, self.y, windowWidth, windowHeight)
        button.move(buttonX, buttonY)
        button.setStyleSheet("border-radius: 3px; height:40px; width:60px; background-color: {}".format("#" + color))
        button.clicked.connect(lambda:self.printName(button))
        self.num_buttons += 1
        button.show()
        self.update()

    @pyqtSlot()
    def printName(self, button):
        pyperclip.copy(button.text())




class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.flowLayout = FlowLayout()
        addColorButton = QPushButton("+", self)
        addColorButton.clicked.connect(self.addButton)
        addColorButton.setStyleSheet("border-radius: 3px; height:40px; width:60px; background-color: #FFFFF6;")
        self.flowLayout.addWidget(addColorButton)
        self.setLayout(self.flowLayout)
        self.setWindowTitle("Pallet")
        self.setAttribute(Qt.WA_TranslucentBackground);

    @pyqtSlot()
    def addButton(self):
        color = getClickColor()
        button = QPushButton("#"+color, self)
        button.setStyleSheet("border-radius: 3px; height:40px; width:60px; background-color: {}".format("#" + color))
        button.clicked.connect(lambda:self.printName(button))
        self.flowLayout.addWidget(button)
        if self.flowLayout.count() <= 8:
            self.setGeometry(QRect(self.pos().x(), self.pos().y(), self.flowLayout.count()*60, self.frameGeometry().height()))
        elif self.flowLayout.count() > 8:
            self.setGeometry(QRect(self.pos().x(), self.pos().y(), self.frameGeometry().width(), 80))
        elif self.flowLayout.count() > 16:
            self.setGeometry(QRect(self.pos().x(), self.pos().y(), self.frameGeometry().width(), 120))

    @pyqtSlot()
    def printName(self, button):
        pyperclip.copy(button.text())

    def moveEvent(self, e):
        self.x = self.pos().x()
        self.y = self.pos().y()
        super(Window, self).moveEvent(e)

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=0):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return False

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize(60, 40)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()



class Click_Coordinates():
    def __init__(self, arr):
        self.x = arr[0]
        self.y = arr[1]

    def __str__(self):
        return f'x:{self.x} y:{self.y}'


def getClickColor():
    coords = coord.coordinates()
    c = Click_Coordinates([x for x in coords])
    rgb_test = color.makeHex(c.x, c.y)
    rgb_test = f'{rgb_test:x}'
    return rgb_test

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Window()
    ui.show()
    sys.exit(app.exec_())
