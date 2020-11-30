import sys
import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPalette
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from win32api import GetSystemMetrics, GetKeyState

from window_manager import WindowManager


class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        full_width, full_height = GetSystemMetrics(0), GetSystemMetrics(1)

        self.setFixedSize(full_width, full_height)
        img = Image.new('RGB', (full_width, full_height))
        img.putalpha(100)
        img.save('test.png')
       
        image = QPixmap('test.png')
        self.main_back = QLabel(self)
        self.main_back.resize(full_width, full_height)
        self.main_back.setPixmap(image)
        self.main_back.show()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.SplashScreen)

        self.WM = WindowManager()
        
        self.timer = QTimer(self)
        self.timer.start(300)
        self.timer.timeout.connect(self.run)

        self.pre_window = None


    def run(self):
        cur_window = self.WM.get_fore_window()
        if cur_window != self.pre_window:
            self.pre_window = cur_window
            print("aoeu")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    AWD = Main()
    AWD.show()
    sys.exit(app.exec_())