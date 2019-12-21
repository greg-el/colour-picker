import sys
from os import getenv
import time
import ctypes
from Xlib import X, display
#from PyQt5 import QtWidgets
coord = ctypes.CDLL('./coords.so')
coord.coordinates.restype = ctypes.c_int * 2
get_RGB = ctypes.CDLL('./color.so')
get_RGB.rgb.argtypes = [ctypes.c_int, ctypes.c_int]
get_RGB.rgb.restype = ctypes.c_uint * 3


class RGB_Values():
    def __init__(self, arr):
        self.r = arr[0]
        self.g = arr[1]
        self.b = arr[2]
    
    def __str__(self):
        return f'r:{self.r} g:{self.g} b:{self.b}'

class Click_Coordinates():
    def __init__(self, arr):
        self.x = arr[0]
        self.y = arr[1]

    def __str__(self):
        return f'x:{self.x} y:{self.y}'


if __name__ == "__main__":
    coords = coord.coordinates()
    c = Click_Coordinates([x for x in coords])
    rgb_test = get_RGB.rgb(c.x, c.y)
    for i in rgb_test:
        print(i)
    test_color = RGB_Values([x for x in rgb_test]) #TODO blue is always wrong and i dont know why

    
