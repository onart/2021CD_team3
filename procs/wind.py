'''
활성 윈도우 이름
'''
import time, ctypes

IDE_LIST=('Visual Studio Code', 'Microsoft Visual Studio')
IDE_REPR=('VS Code', 'VS')

cur='others'

def wname(s):
    for i in range(len(IDE_LIST)):
        if s.find(IDE_LIST[i],-len(IDE_LIST[i])) != -1:
            return IDE_REPR[i]
    return 'others'

def currentWindow(receiver):    #스레드 함수
    lib=ctypes.windll.LoadLibrary('user32.dll')
    while True:
        hwnd = lib.GetForegroundWindow()
        buffer = ctypes.create_unicode_buffer(255)
        lib.GetWindowTextW(hwnd, buffer, ctypes.sizeof(buffer))
        wind = wname(buffer.value)
        if wind != receiver.activeWindow.text:
            receiver.activeWindow.setText(wind)
            # print(cur)
        time.sleep(0.2)   # 갱신 시간 수

if __name__ == '__main__':
    currentWindow()
