'''
활성 윈도우 이름
'''
import time, ctypes

IDE_LIST=('Visual Studio Code', 'Microsoft Visual Studio')
IDE_REPR=('VS Code', 'VS')

cur=''

def wname(s):
    for i in range(len(IDE_LIST)):
        if s.find(IDE_LIST[i],-len(IDE_LIST[i])) != -1:
            return IDE_REPR[i]
    return 'others'

def currentWindow():    #스레드 함수
    global cur
    lib=ctypes.windll.LoadLibrary('user32.dll')
    while True:
        hwnd = lib.GetForegroundWindow()
        buffer = ctypes.create_unicode_buffer(255)
        lib.GetWindowTextW(hwnd, buffer, ctypes.sizeof(buffer))
        wind = wname(buffer.value)
        if wind != cur:
            cur = wind
            # print(cur)
        time.sleep(1)   # 갱신 시간 수

if __name__ == '__main__':
    currentWindow()
