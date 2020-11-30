import win32gui

class WindowManager:
    def window_enum_handler(self, hwnd, resultList):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != '':
            resultList.append((hwnd, win32gui.GetWindowText(hwnd)))
    
    def get_windows(self, handles=[]):
        current_windows = []
        win32gui.EnumWindows(self.window_enum_handler, handles)
        for handle in handles:
            current_windows.append(handle[1])

        return set(current_windows)

    def get_fore_window(self):
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())

    def find_winndow(self, name):
        hwnd = win32gui.FindWindow(None, name)

        return hwnd
    
    def set_window(self, hwnd):
        win32gui.SetForegroundWindow(hwnd)


if __name__ == "__main__":
    WM = WindowManager()
    current_windows = WM.get_windows()
    print(WM.get_fore_window())
    # for window in current_windows:
    #     print(window)