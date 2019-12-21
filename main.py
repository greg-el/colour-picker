import sys
from os import getenv
import time
import ctypes
from Xlib import X, display
#from PyQt5 import QtWidgets

coord = ctypes.CDLL('./obj/coords.so')
coord.coordinates.restype = ctypes.c_int * 2

color = ctypes.CDLL('./obj/color.so')
color.makeHex.restype = ctypes.c_ulong
color.makeHex.argtypes = [ctypes.c_int, ctypes.c_int]

class Click_Coordinates():
    def __init__(self, arr):
        self.x = arr[0]
        self.y = arr[1]

    def __str__(self):
        return f'x:{self.x} y:{self.y}'


if __name__ == "__main__":
    coords = coord.coordinates()
    c = Click_Coordinates([x for x in coords])
    rgb_test = color.makeHex(c.x, c.y)
    test = f'{rgb_test:x}'
    print(test)

    
