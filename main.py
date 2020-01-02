import ctypes
import pyperclip
import sys


from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal, QEvent
from PyQt5.QtWidgets import QApplication, QLayout, QPushButton, QSizePolicy, QWidget

coord = ctypes.CDLL('./obj/coords.so')
coord.coordinates.restype = ctypes.c_int * 2

color = ctypes.CDLL('./obj/color.so')
color.getColor.restype = ctypes.POINTER(ctypes.c_int)
color.getColor.argtypes = [ctypes.c_int, ctypes.c_int]

#TODO: fix when rgb colours get converted to a hex 100 and break the colour picking
#TODO: make a multi-pick function, not sure if its gunna be C++ or python
#TODO: make the window snap to a multiple of the button size after a resize event




class Window(QWidget):
    resized = pyqtSignal()

    def __init__(self):
        super(Window, self).__init__()

        self.x = self.pos().x()
        self.y = self.pos().y()
        self.flowLayout = FlowLayout()
        self.row_max = 8
        self.manual_resize = 0
        self.resized.connect(self.onResize)
        add_color_button = QPushButton("+", self)
        add_color_button.clicked.connect(self.add_color_handle)
        add_color_button.setStyleSheet("""
            border-radius: 5px;
            font-size: 20px;
            height:40px; width:60px;
            color: rgba(255, 255, 255, 255);
            background-color: rgba(255, 255, 255, 30);
        """)

        self.flowLayout.addWidget(add_color_button)
        self.setLayout(self.flowLayout)
        self.setWindowTitle("Pallete")
        self.setAttribute(Qt.WA_TranslucentBackground);

    def add_color_handle(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.multi_add()
        else:
            self.add_button()

    def multi_add(self):
        end = True
        while end:
            self.add_button()
            self.set_window_size()
            if self.flowLayout.count() > 16:
                end = False

    def create_button(self):
        rgb_color = rgb_click_color()
        if rgb_color:
            hex_color = rgb_to_hex(rgb_color.r, rgb_color.g, rgb_color.b)
            darken_text = darkenColor(rgb_color.r, rgb_color.g, rgb_color.b)
            text_color = rgb_to_hex(darken_text.r, darken_text.g, darken_text.b)
            if (rgb_color.r * 0.299 + rgb_color.g * 0.587 + rgb_color.b * 0.114) < 149:
                lighten_text = lightenColor(rgb_color.r, rgb_color.g, rgb_color.b)
                text_color = rgb_to_hex(lighten_text.r, lighten_text.g, lighten_text.b)

            button = QPushButton(hex_color, self)
            button.clicked.connect(lambda: pyperclip.copy(button.text()))
            button.setContextMenuPolicy(Qt.CustomContextMenu)
            button.customContextMenuRequested.connect(lambda: self.remove_button(button))
            button.setStyleSheet(
                f"border-radius: 5px; height:40px; width:60px; background-color: {hex_color}; color: {text_color};")
            button.setProperty("colour", hex_color)
            return button
        return False

    def add_button(self):
        self.manual_resize = 0
        button = self.create_button()
        if button:
            self.flowLayout.addWidget(button)
            self.set_window_size()

        self.manual_resize = 1

    def remove_button(self, button):
        self.manual_resize = 0
        button.setParent(None)
        self.set_window_size()
        self.manual_resize = 1

    def set_window_size(self):
        print(self.flowLayout.count())
        horizontal = self.frameGeometry().width()
        if self.flowLayout.count() <= self.row_max:
            horizontal = self.flowLayout.count()*60+1

        self.setGeometry(QRect(self.pos().x(), self.pos().y(), horizontal, self.get_row_count()*41-1))

    def get_row_count(self):
        return int(((self.flowLayout.count()-1)/self.row_max)+1)

    def moveEvent(self, e):
        self.x = self.pos().x()
        self.y = self.pos().y()
        super(Window, self).moveEvent(e)

    def resizeEvent(self, e):
        self.resized.emit()
        return super(Window, self).resizeEvent(e)

    def onResize(self):
        if self.manual_resize == 1:
            new_row_max = int(self.frameGeometry().width() / 60)
            self.row_max = new_row_max


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


class ClickCoordinates:
    def __init__(self, arr):
        self.x = arr[0]
        self.y = arr[1]

    def __str__(self):
        return f'x:{self.x} y:{self.y}'


class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


def lightenColor(r, g, b):
    color_factor = 70
    if r+color_factor < 255:
        r = r+color_factor
    else:
        r = 255
    if g+color_factor < 255:
        g = g+color_factor
    else:
        g = 255
    if b+color_factor < 255:
        b = b+color_factor
    else:
        b = 255
    return RGB(r, g, b)


def darkenColor(r, g, b):
    color_factor = 100
    if r-color_factor > 0:
        r = r-color_factor
    else:
        r = 0
    if g-color_factor > 0:
        g = g-color_factor
    else:
        g = 0
    if b-color_factor > 0:
        b = b-color_factor
    else:
        b = 0
    return RGB(r, g, b)


def rgb_click_color():
    coords = coord.coordinates()
    c = ClickCoordinates([x for x in coords])
    if c.x == -1 and c.y == -1:
        return False
    r = ctypes.c_int(0)
    g = ctypes.c_int(0)
    b = ctypes.c_int(0)
    color.getColor(c.x, c.y, ctypes.byref(r), ctypes.byref(g), ctypes.byref(b))
    return RGB(round(r.value/256), round(g.value/256), round(b.value/256))


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Window()
    ui.show()
    sys.exit(app.exec_())
