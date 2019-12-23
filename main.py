import sys
from os import getenv
import time
import ctypes
import pyperclip
from Xlib import X, display
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtCore import pyqtSlot, QRect, Qt


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
        self.addColorButton.clicked.connect(self.addButton)
        self.addColorButton.setStyleSheet("border-radius: 3px; height:40px; width:60px; background-color: #FFFFF6;")

        #addColorButton.setStyleSheet(open('mystylesheet.css').read())
        self.setAttribute(Qt.WA_TranslucentBackground);
        self.setGeometry(300, 300, 1, 1)
        self.addColorButton.show()
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
            windowHeight = 40
            addColorButtonX = 60+self.num_buttons*60
            windowWidth = 60+buttonX+60
        elif self.num_buttons >= 8:
            buttonX = (self.num_buttons-8)*60
            buttonY = 80
        
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
    ui = UI()
    sys.exit(app.exec_())
    



    
