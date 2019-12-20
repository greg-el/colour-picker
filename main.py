import sys
import os
from ctypes import *

click = cdll.LoadLibrary("./test.so")
click.argtypes
click.getClickCoordinates()


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Xlib import X, display
from PyQt5 import QtWidgets

def get_coordinates():
    d = display.Display()
    screen = display.screen()
    win = X.PointerWindow
    screen.root.xinput_select_events([xinput.AllDevices])
    while True:
        event = display.next_event()
        print(event)
        if event.type == ButtonPress:
            print(event.xbutton.button)

app = QtWidgets.QApplication(sys.argv)
add_button = QtWidgets.QPushButton("Add")



sys.exit(app.exec_())