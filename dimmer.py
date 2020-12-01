import sys
import time
import numpy as np
from PIL import Image
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPalette
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from win32com import client
from win32api import GetSystemMetrics, GetKeyState

from window_manager import WindowManager
from RNN import RNN



LIST = ['python', '파일']

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
        self.pre_window = self.WM.get_fore_window()
        self.rnn = RNN()
        self.latest_windows = []
        
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.run)

        self.timer2 = QTimer(self)
        self.timer2.start(3600000)
        self.timer2.timeout.connect(self.train)

    def run(self):
        try:
            with open("data.txt", 'a') as f:
                cur_window = self.WM.get_fore_window().split()[0]
                if cur_window != self.pre_window and cur_window != 'python':
                    print(cur_window)
                    self.pre_window = cur_window
                    f.write(" "+cur_window)
                    #target_windows = self.rnn.test(['계산기', '파일'], 3)
                    target_windows = self.temp_target(cur_window)
                    target_windows.append(cur_window)
                    print(target_windows)
                    self.WM.set_window(self.WM.find_window('python'))
                    all_windows = list(self.WM.get_windows())
                    for t_window in target_windows:
                        for i, window in enumerate(all_windows):
                            if t_window == window.split()[0] and t_window not in LIST:
                                self.WM.set_window(self.WM.find_window(all_windows[i]))
        except:
            pass

    def train(self):
        self.rnn = RNN()
        self.rnn.train()

    def temp_target(self, cur_window):
        target_windows = []
        if cur_window == 'Towards':
            target_windows.append('번역')
            target_windows.append('[2020.02.00]')
        elif cur_window == '번역':
            target_windows.append('Towards')
            target_windows.append('[2020.02.00]')
        elif cur_window == '[2020.02.00]':
            target_windows.append('Towards')
            target_windows.append('번역')
        elif cur_window == '카카오톡':
            target_windows.append('YouTube')
            target_windows.append('계산기')
        elif cur_window == 'YouTube':
            target_windows.append('카카오톡')
            target_windows.append('계산기')
        elif cur_window == '계산기':
            target_windows.append('YouTube')
            target_windows.append('카카오톡')
        
        return target_windows


if __name__ == '__main__':
    app = QApplication(sys.argv)
    AWD = Main()
    AWD.show()
    sys.exit(app.exec_())