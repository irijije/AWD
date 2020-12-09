import os
import sys
import time
import numpy as np
from PIL import Image
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QPixmap, QPalette, QIcon
from PyQt5.QtWidgets import QMessageBox, QApplication, QLabel, QMainWindow, QPushButton, QSystemTrayIcon
from win32com import client
from win32api import GetSystemMetrics, GetKeyState

from window_manager import WindowManager
from RNN import RNN


LIST = ['dimmer', '파일']
form_class = uic.loadUiType("ui/main.ui")[0]


class Main(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon('ui/icon.png'))
        self.trayIcon.activated.connect(self.restore_window)

        self.WM = WindowManager()
        self.pre_window = self.WM.get_fore_window()
        self.rnn = RNN()
        
        self.startButton.clicked.connect(self.btn_clk_start)
        self.startState = True
        self.trainButton.clicked.connect(self.btn_clk_train)
        self.helpButton.clicked.connect(self.btn_clk_help)

    def minimize_window(self, event):
        if (event.type() == QEvent.WindowStateChange and 
                self.isMinimized()):
            self.setWindowFlags(self.windowFlags() & ~Qt.Tool)
            self.trayIcon.show()
            return True
        else:
            return super(Main, self).minimize_window(event)

    def restore_window(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.trayIcon.hide()
            self.showNormal()

    def btn_clk_start(self):
        if self.startState == True:
            self.startState = False
            self.startButton.setText('Stop')
            
            self.back = Background()
            self.back.show()
            self.trayIcon.setVisible(True)
            self.hide()

            self.timer = QTimer(self)
            self.timer.start(1000)
            self.timer.timeout.connect(self.run)

            self.timer2 = QTimer(self)
            self.timer2.start(3600000)
            self.timer2.timeout.connect(self.train)
        else:
            self.startState = True
            self.startButton.setText('Start')
            self.back.close()
            self.timer.stop()
            self.timer2.stop()

    def btn_clk_train(self):
        self.trainButton.setEnabled(False)
        try:
            os.remove('params.pkl')
        except:
            pass
        time.sleep(1)
        self.rnn.train()
        QMessageBox.information(self, "RNN", "train finished")
        self.trainButton.setEnabled(True)

    def btn_clk_help(self):
        QMessageBox.information(self, "Help", "wnsrud3611@gmail.com")

    def run(self):
        try:
            with open("data.txt", 'a') as f:
                cur_window = self.WM.get_fore_window().split()[0]
                if cur_window != self.pre_window and cur_window != 'dimmer':
                    self.pre_window = cur_window
                    f.write(" "+cur_window)
                    target_windows = list(self.rnn.test([cur_window], 5))
                    target_windows.append(cur_window)
                    print(target_windows)
                    self.WM.set_window(self.WM.find_window('dimmer'))
                    all_windows = list(self.WM.get_windows())
                    for t_window in target_windows:
                        for i, window in enumerate(all_windows):
                            if t_window == window.split()[0] and t_window not in LIST:
                                self.WM.set_window(self.WM.find_window(all_windows[i]))
        except:
            pass

    def train(self):
        try:
            os.remove('params.pkl')
        except:
            pass
        time.sleep(1)
        self.rnn.train()


class Background(QMainWindow):
    def __init__(self):
        super().__init__()

        full_width, full_height = GetSystemMetrics(0), GetSystemMetrics(1)

        self.setFixedSize(full_width, full_height)
        img = Image.new('RGB', (full_width, full_height))
        img.putalpha(100)
        img.save('ui/background.png')
       
        image = QPixmap('ui/background.png')
        self.main_back = QLabel(self)
        self.main_back.resize(full_width, full_height)
        self.main_back.setPixmap(image)
        self.main_back.show()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.SplashScreen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    AWD = Main()
    AWD.show()
    sys.exit(app.exec_())