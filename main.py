import ctypes
import pyperclip
import sys
import time

from os import getenv
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QLayout, QPushButton, QSizePolicy, QWidget)
from Xlib import X, display

coord = ctypes.CDLL('./obj/coords.so')
coord.coordinates.restype = ctypes.c_int * 2

color = ctypes.CDLL('./obj/color.so')
color.getColor.restype = ctypes.POINTER(ctypes.c_int)
color.getColor.argtypes = [ctypes.c_int, ctypes.c_int]

#TODO: fix when rgb colours get converted to a hex 100 and break the colour picking
#TODO: make a multi-pick function, not sure if its gunna be C++ or python


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.flowLayout = FlowLayout()
        addColorButton = QPushButton("+", self)
        addColorButton.clicked.connect(self.addButton)
        addColorButton.setStyleSheet("border-radius: 5px; font-size: 20px; height:40px; width:61px; color: rgba(255, 255, 255, 255); background-color: rgba(255, 255, 255, 30);")
        self.flowLayout.addWidget(addColorButton)
        self.setLayout(self.flowLayout)
        self.setWindowTitle("Pallet")
        self.setAttribute(Qt.WA_TranslucentBackground);


    @pyqtSlot()
    def addButton(self):
        rgbColor = getRGBClickColor()
        color = rgbToHex(rgbColor.r, rgbColor.g, rgbColor.b)
        button = QPushButton(color, self)
        button.clicked.connect(lambda:self.printName(button))
        colorFactor = 20
        darkenText = darkenColor(rgbColor.r, rgbColor.g, rgbColor.b)
        textColor = rgbToHex(darkenText.r, darkenText.g, darkenText.b)
        if (rgbColor.r*0.299 + rgbColor.g*0.587 + rgbColor.b*0.114) < 149:
            lightenText = lightenColor(rgbColor.r, rgbColor.g, rgbColor.b)
            textColor = rgbToHex(lightenText.r, lightenText.g, lightenText.b)
        self.flowLayout.addWidget(button)
        button.setStyleSheet(f"border-radius: 5px; height:40px; width:61px; background-color: {color}; color: {textColor};")
        print(self.flowLayout.count()*60)

        if self.flowLayout.count() <= 8:
            self.setGeometry(QRect(self.pos().x(), self.pos().y(), self.flowLayout.count()*61+1, self.frameGeometry().height()))
        elif self.flowLayout.count() > 8:
            self.setGeometry(QRect(self.pos().x(), self.pos().y(), self.frameGeometry().width(), 81))
        elif self.flowLayout.count() > 16:
            self.setGeometry(QRect(self.pos().x(), self.pos().y(), self.frameGeometry().width(), 121))
        

    @pyqtSlot()
    def printName(self, button):
        pyperclip.copy(button.text())


    def moveEvent(self, e):
        self.x = self.pos().x()
        self.y = self.pos().y()
        super(Window, self).moveEvent(e)


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=1):
        self.itemList = []
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.arrangeAddButton()


    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.insert(-1, item)

    def count(self):
        return len(self.itemList)

    def arrangeAddButton(self):
        if self.count() >= 2:
            addButton = self.itemList[-2]
            self.itemList.pop(len(self.itemList)-1)
            self.itemList.append(addButton)
        
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


class RGB():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


def lightenColor(r, g, b):
    colorFactor = 70
    if r+colorFactor < 255:
        r = r+colorFactor
    else:
        r = 255
    if g+colorFactor < 255:
        g = g+colorFactor
    else:
        g = 255
    if b+colorFactor < 255:
        b = b+colorFactor
    else:
        b = 255
    return RGB(r, g, b)


def darkenColor(r, g, b):
    colorFactor = 100
    if r-colorFactor > 0:
        r = r-colorFactor
    else:
        r = 0
    if g-colorFactor > 0:
        g = g-colorFactor
    else:
        g = 0
    if b-colorFactor > 0:
        b = b-colorFactor
    else:
        b = 0
    return RGB(r, g, b)


def getRGBClickColor():
    coords = coord.coordinates()
    c = Click_Coordinates([x for x in coords])
    r = ctypes.c_int(0)
    g = ctypes.c_int(0)
    b = ctypes.c_int(0)
    color.getColor(c.x, c.y, ctypes.byref(r), ctypes.byref(g), ctypes.byref(b))
    return RGB(round(r.value/256), round(g.value/256), round(b.value/256))


def rgbToHex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Window()
    ui.show()
    sys.exit(app.exec_())
